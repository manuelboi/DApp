from web3 import Web3
import asyncio


class Wallet:
    # Contract infos
    contract_address = ''
    contract_ABI = ''

    def __init__(self, wallet_address, private_key):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.w3 = Wallet.__configure_infura()
        self.nonce = self.__configure_nonce()
        self.contract = self.__create_contract()
        self.student = None

    @staticmethod
    def __configure_infura():
        w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/a2d3ce8effcf445b8fea9dad109c9150"))
        if not w3.isConnected():
            raise ConnectionError("La connessione al nodo Infura è fallita")
        return w3

    def __configure_nonce(self):
        try:
            nonce = self.w3.eth.getTransactionCount(self.wallet_address)
        except:
            raise "L'indirizzo del wallet non è valido"
        return nonce

    def __create_contract(self):
        return self.w3.eth.contract(address=self.contract_address, abi=self.contract_ABI)

    def __send_transaction(self):
        transaction = self.contract.functions.emitDataRequestEvent().buildTransaction(
            {"chainId": 5, "from": self.wallet_address, "nonce": self.nonce})

        # Sign transaction
        signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)

        # Send transaction
        self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    def handle_event(self, event):
        self.student = self.contract.functions.requestData().call()

    async def __log_loop(self, event_filter, poll_interval):
        while True:
            for PairCreated in event_filter.get_new_entries():
                self.handle_event(PairCreated)
            await asyncio.sleep(poll_interval)

    def __wait_for_answer(self):
        event_filter = self.contract.events.dataReadyEvent.createFilter(fromBlock='latest')
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.__log_loop(event_filter, 2)))
        finally:
            loop.close()

    def request_data(self):
        self.__send_transaction()
        self.__wait_for_answer()
