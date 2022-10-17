from web3 import Web3
import asyncio


class Wallet:
    # Contract infos
    contract_address = '0x054a49AB33d9520F03593b7c9b5abb24BbbECBA1'
    contract_ABI = '[ { "inputs": [], "stateMutability": "nonpayable", "type": "constructor" }, { "anonymous": false, ' \
                   '"inputs": [], "name": "dataReadyEvent", "type": "event" }, { "anonymous": false, "inputs": [ { ' \
                   '"indexed": false, "internalType": "address", "name": "adr", "type": "address" } ], ' \
                   '"name": "dataRequestEvent", "type": "event" }, { "inputs": [], "name": "emitDataReadyEvent", ' \
                   '"outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], ' \
                   '"name": "emitDataRequestEvent", "outputs": [], "stateMutability": "nonpayable", ' \
                   '"type": "function" }, { "inputs": [ { "components": [ { "internalType": "string", "name": "id", ' \
                   '"type": "string" }, { "internalType": "string", "name": "name", "type": "string" }, ' \
                   '{ "internalType": "string", "name": "surname", "type": "string" } ], "internalType": "struct ' \
                   'StudentCurriculum.Student", "name": "student", "type": "tuple" } ], "name": "setData", ' \
                   '"outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], ' \
                   '"name": "requestData", "outputs": [ { "components": [ { "internalType": "string", "name": "id", ' \
                   '"type": "string" }, { "internalType": "string", "name": "name", "type": "string" }, ' \
                   '{ "internalType": "string", "name": "surname", "type": "string" } ], "internalType": "struct ' \
                   'StudentCurriculum.Student", "name": "student", "type": "tuple" } ], "stateMutability": "view", ' \
                   '"type": "function" } ] '

    def __init__(self, wallet_address, private_key):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.w3 = Wallet.__configure_infura()
        self.nonce = self.__configure_nonce()
        self.contract = self.__create_contract()
        self.student = None
        self.loop = False

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
        if event.args['adr'] == self.wallet_address:
            self.student = self.contract.functions.requestData().call()
            self.loop = False

    async def __log_loop(self, event_filter, poll_interval):
        self.loop = True
        while self.loop is True:
            for PairCreated in event_filter.get_new_entries():
                self.handle_event(PairCreated)
            await asyncio.sleep(poll_interval)

    def __wait_for_answer(self):
        event_filter = self.contract.events.dataReadyEvent.createFilter(fromBlock='latest')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.__log_loop(event_filter, 2)))
        finally:
            loop.close()

    def request_data(self):
        self.__send_transaction()
        self.__wait_for_answer()
