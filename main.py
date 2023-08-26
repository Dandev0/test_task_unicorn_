import aiohttp
from config import *
import asyncio
from arg import Args


class Get_valute:
    def __init__(self):
        self.period = period
        self.old_exchange_rate = {
                    'rub': None,
                    'usd': None,
                    'eur': None
                }

    async def take_value_valutes(self, url):
        async with aiohttp.ClientSession() as request:
            async with request.get(url) as response:
                response_valute = await response.json()
                self.new_data_valute = {
                    'rub': response_valute['rates']['RUB'],
                    'usd': response_valute['rates']['USD'],
                    'eur': response_valute['rates']['EUR']
                }
                global all_info_about_valute
                all_info_about_valute = {'old_valute': self.old_exchange_rate, 'actual_valute': self.new_data_valute}

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
        self.post_data = post_data
        self.need_valute = need_valute

    async def check_change_valute(self):
        await asyncio.sleep(2)
        if self.old_balance != self.balance:
            logger.warning(
                f'Balance has been changed!\nOld balance: {self.old_balance}\nActual balance: {self.balance}')
            for i in self.old_balance.keys():
                self.old_balance[i] = self.balance[i]
        if all_info_about_valute['actual_valute'] != all_info_about_valute['old_valute']:
            logger.warning(
                f'Currency exchange rate has been changed!\nOld сurrency exchange rate: {all_info_about_valute["old_valute"]}\nActual сurrency exchange rate: {all_info_about_valute["actual_valute"]}')
            for i in all_info_about_valute['actual_valute'].keys():
                all_info_about_valute['old_valute'][i] = all_info_about_valute['actual_valute'][i]
        await asyncio.sleep(58)
        loop.create_task(self.check_change_valute())

    async def set_balance(self):
        for i in self.post_data.keys():
            self.balance[i] = self.post_data[i]
        return self.balance

    async def get_balance(self):
        return self.balance

    async def get_need_valute(self):
        return self.balance[self.need_valute]

    async def modify_balance(self):
        for i in self.post_data.keys():
            balance[i] += self.post_data[i]
        return balance

    async def sum_every_valutes(self):
        self.rub_balance = balance['rub']
        self.usd_balance = balance['usd']
        self.eur_balance = balance['eur']
        self.data_exchange_rate = all_info_about_valute['actual_valute']
        self.sum_rub = self.rub_balance + self.usd_balance * self.data_exchange_rate['rub'] + self.eur_balance * self.data_exchange_rate['eur'] * self.data_exchange_rate['rub']
        self.sum_usd = self.usd_balance + self.rub_balance / self.data_exchange_rate['rub'] + self.eur_balance * self.data_exchange_rate['eur']
        self.sum_eur = (self.rub_balance / self.data_exchange_rate['rub'] + self.usd_balance) * self.data_exchange_rate['eur'] + self.eur_balance
        response = {'rub': round(self.sum_rub, 2), 'usd': round(self.sum_usd, 2), 'eur': round(self.sum_eur, 2)}
        return response


async def background_tasks(app):
    get_valute = Get_valute()
    check_change = Balance()
    app['task'] = asyncio.create_task(get_valute.start_get_valute())
    app['task1'] = asyncio.create_task(check_change.check_change_valute())


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
        return web.Response(text=f'На рублевом счете: {balance["rub"]} рублей,\n'
                                 f'На долларовом счете: {balance["usd"]} долларов,\n'
                                 f'На евро счете: {balance["eur"]} евро',
                            headers={"content-type": "text/plain"})

    async def modify_balance(self, request):
        data = await request.json()
        updated_balance = await Balance(post_data=data).modify_balance()
        return web.Response(text=f'Баланс кошельков изменен!\nНовый баланс: {updated_balance}', headers={"content-type": "text/plain"})

    async def get_amount(self, request):
        balances = await Balance().sum_every_valutes()
        text = f'Баланс в рублях: {balances["rub"]},\nБаланс в долларах: {balances["usd"]},\nБаланс в евро: {balances["eur"]}'
        return web.Response(text=f'Балансы кошельков:\n{text}', headers={"content-type": "text/plain"})


if __name__ == '__main__':
    api = API()
    args = Args().get_args()
    old_balance = {'rub': args.rub, 'usd': args.usd, 'eur': args.eur}
    balance = {'rub': args.rub, 'usd': args.usd, 'eur': args.eur}
    period = args.period
    logger.debug('App is started')
    if args.debug.lower() in {'1', 'true', 'y'}:
        logger.info('Logger is active')
    elif args.debug.lower() in {'0', 'false', 'n'}:
        logger.info('Logger is inactive!')
        logger.disabled = True
    loop = asyncio.get_event_loop()
    data_valute_ = {}
    app.add_routes([web.post('/amount/set', api.set_balance),
                    web.get('/rub/get', api.get_rub),
                    web.get('/eur/get', api.get_eur),
                    web.get('/usd/get', api.get_usd),
                    web.get('/amount/get', api.get_amount),
                    web.post('/modify', api.modify_balance),
                    web.get('/', api.get_balance_all_valutes)
                    ])
    start_server()
