from web3 import Web3
import asyncio
import datetime


class Wallet:
    # Contract infos
    contract_address = '0x9f239F155822C95C556AD89525213F940379D336'
    contract_ABI = '[ { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "adr", ' \
                   '"type": "address" } ], "name": "dataReadyEvent", "type": "event" }, { "anonymous": false, ' \
                   '"inputs": [ { "indexed": false, "internalType": "address", "name": "adr", "type": "address" } ], ' \
                   '"name": "dataRequestEvent", "type": "event" }, { "inputs": [ { "internalType": "address", ' \
                   '"name": "adr", "type": "address" } ], "name": "emitDataReadyEvent", "outputs": [], ' \
                   '"stateMutability": "nonpayable", "type": "function" }, { "inputs": [], ' \
                   '"name": "emitDataRequestEvent", "outputs": [], "stateMutability": "nonpayable", ' \
                   '"type": "function" }, { "inputs": [], "name": "requestData", "outputs": [ { "components": [ { ' \
                   '"internalType": "string", "name": "name", "type": "string" }, { "internalType": "string", ' \
                   '"name": "surname", "type": "string" }, { "components": [ { "internalType": "string", ' \
                   '"name": "id", "type": "string" }, { "internalType": "string", "name": "studyCourse", ' \
                   '"type": "string" }, { "internalType": "int256", "name": "completed", "type": "int256" }, ' \
                   '{ "components": [ { "internalType": "int256", "name": "mark", "type": "int256" }, ' \
                   '{ "internalType": "uint256", "name": "date", "type": "uint256" }, { "internalType": "string", ' \
                   '"name": "teaching", "type": "string" } ], "internalType": "struct StudentCurriculum.Exam[]", ' \
                   '"name": "exams", "type": "tuple[]" } ], "internalType": "struct StudentCurriculum.Career[]", ' \
                   '"name": "careers", "type": "tuple[]" } ], "internalType": "struct StudentCurriculum.Student", ' \
                   '"name": "student", "type": "tuple" } ], "stateMutability": "nonpayable", "type": "function" }, ' \
                   '{ "inputs": [ { "components": [ { "internalType": "string", "name": "name", "type": "string" }, ' \
                   '{ "internalType": "string", "name": "surname", "type": "string" }, { "components": [ { ' \
                   '"internalType": "string", "name": "id", "type": "string" }, { "internalType": "string", ' \
                   '"name": "studyCourse", "type": "string" }, { "internalType": "int256", "name": "completed", ' \
                   '"type": "int256" }, { "components": [ { "internalType": "int256", "name": "mark", ' \
                   '"type": "int256" }, { "internalType": "uint256", "name": "date", "type": "uint256" }, ' \
                   '{ "internalType": "string", "name": "teaching", "type": "string" } ], "internalType": "struct ' \
                   'StudentCurriculum.Exam[]", "name": "exams", "type": "tuple[]" } ], "internalType": "struct ' \
                   'StudentCurriculum.Career[]", "name": "careers", "type": "tuple[]" } ], "internalType": "struct ' \
                   'StudentCurriculum.Student", "name": "student", "type": "tuple" }, { "internalType": "address", ' \
                   '"name": "adr", "type": "address" } ], "name": "setData", "outputs": [], "stateMutability": ' \
                   '"nonpayable", "type": "function" } ] '

    def __init__(self, private_key):
        self.__configure_infura()
        self.private_key = private_key
        self.wallet_address = self.w3.eth.account.from_key(private_key).address
        self.contract = self.__create_contract()
        self.student = None
        self.loop = False  # Used to stop loop when data is received

    def __configure_infura(self):
        self.w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/a2d3ce8effcf445b8fea9dad109c9150"))
        if not self.w3.isConnected():
            raise ConnectionError("La connessione al nodo Infura è fallita")
        return self.w3

    def __create_contract(self):
        return self.w3.eth.contract(address=self.contract_address, abi=self.contract_ABI)

    def __send_transaction(self):
        nonce = self.w3.eth.getTransactionCount(self.wallet_address)

        transaction = self.contract.functions.emitDataRequestEvent().buildTransaction(
            {"chainId": 5, "from": self.wallet_address, "nonce": nonce})

        # Sign transaction
        signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)

        # Send transaction
        self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    def handle_event(self, event):
        if event.args['adr'] == self.wallet_address:
            student = self.contract.functions.requestData().call({"from": self.wallet_address})

            careers = []
            for career in student[2]:
                exams = []
                for exam in career[3]:
                    final_exam = (exam[0], datetime.datetime.fromtimestamp(exam[1] / 1e3), exam[2])
                    exams.append(final_exam)
                final_career = (career[0], career[1], career[2], exams)
                careers.append(final_career)
            self.student = (student[0], student[1], careers)
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
