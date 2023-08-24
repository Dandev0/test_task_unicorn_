import aiohttp
from config import *
import asyncio
from arg import Args


class Get_valute:
    def __init__(self):
        self.period = args.period
        self.old_data_valute = None

    async def take_value_valutes(self, url):
        async with aiohttp.ClientSession() as request:
            async with request.get(url) as response:
                response_valute = await response.json()
                self.new_data_valute = {
                    'RUB': response_valute['rates']['RUB'],
                    'USD': response_valute['rates']['USD'],
                    'EUR': response_valute['rates']['EUR']
                }
                global all_info_about_valute
                all_info_about_valute = {'old_valute': self.old_data_valute, 'actual_valute': self.new_data_valute}
                for i in self.new_data_valute.keys():
                    self.old_data_valute[i] = self.new_data_valute[i]

    async def start_get_valute(self):
        url = f"https://openexchangerates.org/api/latest.json?app_id=3d3a6f24e1644a66a070bd8af9e6aaec&base=USD"
        loop.create_task(self.take_value_valutes(url=url))
        await asyncio.sleep(self.period * 60)
        loop.create_task(self.start_get_valute())


class Balance(Get_valute):
    def __init__(self, post_data=None, need_valute=None):
        super().__init__()
        self.old_balance = old_balance
        self.balance = balance
        self.base_valute = 'USD'
        self.post_data = post_data
        self.need_valute = need_valute

    async def check_change_valute(self):
        if self.old_balance != self.balance:
            logger.warning(
                f'Balance has been changed!\nOld balance: {self.old_balance}\nActual balance: {self.balance}')
        if self.all_info_about_valute['actual_valute'] != self.all_info_about_valute['old_valute']:
            logger.warning(
                f'Currency exchange rate has been changed!\nOld сurrency exchange rate: {self.old_data_valute}\nActual сurrency exchange rate: {self.new_data_valute}')
        await asyncio.sleep(20)

    async def set_balance(self):
        for i in self.post_data.keys():
            balance[i] = self.post_data[i]
        return balance

    async def get_balance(self):
        return self.balance

    async def get_need_valute(self):
        return self.balance[self.need_valute]

    async def modify_balance(self):
        for i in self.post_data.keys():
            balance[i] += self.post_data[i]
        return balance

    async def sum_every_valutes(self):
        self.rub = balance['rub']
        self.usd = balance['usd']
        self.eur = balance['eur']
        self.sum_rub = self.rub + self.usd * self.new_data_valute['rub'] + self.eur * self.new_data_valute['usd'] * self.new_data_valute['rub']
        self.sum_usd = self.usd + self.rub / self.usd + self.eur / self.usd
        resp = [self.sum_rub, self.sum_usd]
        return resp


async def background_tasks(app):
    get_valute = Get_valute()
    app['task'] = asyncio.create_task(get_valute.start_get_valute())
    app['task1'] = asyncio.create_task(Balance().check_change_valute())


def start_server():
    app.on_startup.append(background_tasks)
    app.add_routes(routes)
    web.run_app(app, host='127.0.1.1', port='8080', loop=loop)


class API:
    async def get_eur(self, request):
        eur_balance = await Balance(need_valute='eur').get_need_valute()
        return web.Response(text=f'Евро баланс: {eur_balance}', headers={"content-type": "text/plain"})

    async def get_usd(self, request):
        usd_balance = await Balance(need_valute='usd').get_need_valute()
        return web.Response(text=f'Доллоровый баланс: {usd_balance}', headers={"content-type": "text/plain"})

    async def get_rub(self, request):
        rub_balance = await Balance(need_valute='rub').get_need_valute()
        return web.Response(text=f'Рублевый баланс: {rub_balance}', headers={"content-type": "text/plain"})

    async def set_balance(self, request):
        set_valute_data = await request.json()
        updated_balance = await Balance(post_data=set_valute_data).set_balance()
        return web.Response(text=f'Request: {updated_balance}', headers={"content-type": "text/plain"})

    async def get_balance_all_valutes(self, request):
        balance = await Balance().get_balance()
        return web.Response(text=f'Актуальный  баланс для каждой валюты: {balance}',
                            headers={"content-type": "text/plain"})

    async def modify_balance(self, request):
        data = await request.json()
        updated_balance = await Balance(post_data=data).modify_balance()
        return web.Response(text=f'Баланс кошельков изменен!\nНовый баланс: {updated_balance}')

    async def get_amount(self, request):
        balances = await Balance().sum_every_valutes()
        return web.Response(text=f'Балансы кошельков: {balances}')


if __name__ == '__main__':
    api = API()
    old_balance = None
    args = Args().get_args()
    balance = {'rub': args.rub, 'usd': args.usd, 'eur': args.eur}
    period = args.period
    logger.debug('App is started')
    if args.debug.lower() in {'1', 'true', 'y'}:
        logger.info('Logger is active')
    elif args.debug.lower() in {'0', 'false', 'n'}:
        logger.disabled = True
    loop = asyncio.get_event_loop()
    data_valute_ = {}
    app.add_routes([web.post('/amount/set', api.set_balance),
                    web.get('/get/rub', api.get_rub),
                    web.get('/get/eur', api.get_eur),
                    web.get('/get/usd', api.get_usd),
                    web.get('/amount/get', api.get_amount),
                    web.post('/modify', api.modify_balance),
                    # (web.get('/', api.get_balance))
                    ])
    start_server()
