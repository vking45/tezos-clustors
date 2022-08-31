import smartpy as sp
Mixed = sp.io.import_stored_contract("MixedClustor")


class MixedCreator(sp.Contract):
    def __init__(self):
        self.init(
            clustorList = sp.list([],t=sp.TAddress)
        )
        
    @sp.entry_point
    def default(self):
        sp.failwith("NOT ALLOWED")
        
    @sp.entry_point
    def createClustor(self, params):
        sp.verify(sp.amount >= sp.mutez(5000000), message="Please make sure to send the creation fees of 5 XTZ")
        sp.set_type(params, sp.TRecord(tokenList=sp.TMap(sp.TAddress, sp.TNat), fa2tokens=sp.TMap(sp.TAddress, sp.TPair(sp.TNat, sp.TNat)), clustorName=sp.TString))
        clustor : sp.TAddress = sp.create_contract(contract = Mixed.MixedClustor(creator=sp.sender, tokens=params.tokenList, fa2tokens=params.fa2tokens ,clustorName=params.clustorName))
        self.data.clustorList.push(clustor)
        sp.send(sp.address("tz1iCq9Fv4KXWRKiWft9cdDjcDv4YkcdeNTD"), sp.balance)

    @sp.add_test(name = "ClustorCreator")
    def test():
        scenario = sp.test_scenario()
        scenario.h1("Clustor Creator")
        temp = sp.address("tz1iCq9Fv4KXWRKiWft9cdDjcDv4YkcdeNTD")
        cc = MixedCreator()
        scenario += cc    
        scenario += cc.createClustor(tokenList= sp.map({sp.address("KT1L8uYmESypf5P2Ep2QqS8L4wrB4rB29nnQ") : sp.nat(1000), sp.address("KT1E84As5ycCEEEn3mn6EqoKqUtxYfhC6z3j") : sp.nat(1000)}), fa2tokens=sp.map({sp.address("KT1P6owrsdvgLCHaio7z5dVRmjjhUMhJBcYd") : sp.pair(2149, 1)}) ,clustorName="Test").run(sender=temp, amount=sp.tez(5))
    