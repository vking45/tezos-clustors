import smartpy as sp
FA12 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA1.2.py")

class SwitchClustorFA12(sp.Contract):
    def __init__(
            self,
            creator : sp.TAddress, 
            t1 : sp.TAddress,
            t2 : sp.TAddress,
            plentySwapAddress : sp.TAddress,
            t1amt : sp.TNat,
            t2amt : sp.TNat,
            clustorName : sp.TString,
        ):
        self.init(
            clustorName = clustorName,
            creator = creator,
            t1 = t1,
            t2 = t2,
            plentySwapAddress = plentySwapAddress,
            t1amt = t1amt,
            t2amt = t2amt,
            clustorInited = False,
            clustorToken = sp.address("KT19PC5oj39gqoRs8x69RU6RZzspM4bWpCG2"),
            clustorSupply = sp.nat(0)
        )

    @sp.entry_point
    def initClustorToken(self):
        sp.verify(sp.sender == self.data.creator, message="Only creator can init the clustor_token")
        sp.verify(self.data.clustorInited == False, message="The clustor token has already been inited")
        token_metadata = {    
            "decimals"    : "0"
        }
        token = sp.create_contract(contract = FA12.FA12(admin = sp.self_address, config = FA12.FA12_config(), token_metadata = token_metadata))
        self.data.clustorInited = True
        self.data.clustorToken = token

    @sp.entry_point
    def issueToken(self, amount : sp.TNat):
        sp.verify(self.data.clustorInited == True, message="The clustor must be inited for issuing a clustor token")
        sp.verify(amount > 0, message="Please enter a valid amount of tokens")
        token1_handler = sp.contract(
                            sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))),
                            address=self.data.t1,
                            entry_point="transfer",
                            ).open_some()
        sp.transfer(sp.record(
                            from_= sp.sender,
                            to_= sp.self_address,
                            value= self.data.t1amt * amount
                            ),
                            sp.mutez(0),
                            token1_handler)
        token2_handler = sp.contract(
                            sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))),
                            address=self.data.t2,
                            entry_point="transfer",
                            ).open_some()
        sp.transfer(sp.record(
                            from_= sp.sender,
                            to_= sp.self_address,
                            value= self.data.t2amt * amount
                            ),
                            sp.mutez(0),
                            token2_handler)
        clustor_token_handler = sp.contract(
                            sp.TRecord(address=sp.TAddress,value=sp.TNat),
                            address=self.data.clustorToken,
                            entry_point="mint"
                            ).open_some()
        sp.transfer(sp.record(
                            address=sp.sender,
                            value=amount
                            ),
                            sp.mutez(0),
                            clustor_token_handler)
        ct_supply = sp.contract(
                            sp.TPair(sp.TUnit, sp.TContract(sp.TNat)),
                            self.data.clustorToken,
                            "getTotalSupply",
                            ).open_some()
        sp.transfer(
                            (sp.unit , sp.self_entry_point("setClustorSupply")),
                            sp.tez(0),
                            ct_supply,
                            )

    @sp.entry_point
    def redeemToken(self, amount : sp.TNat):
        sp.verify(self.data.clustorInited == True, message="The clustor must be inited for redeeming a clustor token")              
        sp.verify(amount > 0, message="Please enter a valid amount of tokens")
        clustor_burn_handler = sp.contract(
                            sp.TRecord(address=sp.TAddress,value=sp.TNat),
                            address=self.data.clustorToken,
                            entry_point="burn"
                            ).open_some()
        sp.transfer(sp.record(
                            address=sp.sender,
                            value=amount
                            ),
                            sp.mutez(0),
                            clustor_burn_handler)
        token1_handler = sp.contract(
                            sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))),
                            address=self.data.t1,
                            entry_point="transfer",
                            ).open_some()
        sp.transfer(sp.record(
                            from_= sp.self_address,
                            to_= sp.sender,
                            value= self.data.t1amt * amount
                            ),
                            sp.mutez(0),
                            token1_handler)
        token2_handler = sp.contract(
                            sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))),
                            address=self.data.t2,
                            entry_point="transfer",
                            ).open_some()
        sp.transfer(sp.record(
                            from_= sp.self_address,
                            to_= sp.sender,
                            value= self.data.t2amt * amount
                            ),
                            sp.mutez(0),
                            token2_handler)
        ct_supply = sp.contract(
                            sp.TPair(sp.TUnit, sp.TContract(sp.TNat)),
                            self.data.clustorToken,
                            "getTotalSupply",
                            ).open_some()
        sp.transfer(
                            (sp.unit , sp.self_entry_point("setClustorSupply")),
                            sp.tez(0),
                            ct_supply,
                            )

    @sp.entry_point
    def switchToT2(self, params):
        sp.set_type(params, sp.TRecord(req_amt = sp.TNat))
        sp.verify(sp.sender == self.data.creator, message="Only the creator can change the proportions of tokens")
        sp.verify(self.data.clustorInited == True, message="The clustor must be inited for issuing a clustor token")

        plenty_handler = sp.contract(
                            sp.TRecord(tokenAmountIn = sp.TNat, MinimumTokenOut = sp.TNat, recipient = sp.TAddress, requiredTokenAddress = sp.TAddress, requiredTokenId = sp.TNat),
                            self.data.plentySwapAddress,
                            "Swap",
                            ).open_some()

        sp.transfer(sp.record(
                            tokenAmountIn = self.data.t1amt * self.data.clustorSupply,
                            MinimumTokenOut = params.req_amt * self.data.clustorSupply,
                            recipient = sp.self_address,
                            requiredTokenAddress = self.data.t2,
                            requiredTokenId = sp.nat(0)
                            ),
                            sp.mutez(0),
                            plenty_handler,
                            )

        t1_balance = sp.contract(
                            sp.TPair(sp.TAddress, sp.TContract(sp.TNat)),
                            self.data.t1,
                            "getBalance",
                            ).open_some()
        sp.transfer(
                            (sp.self_address , sp.self_entry_point("setT1Amt")),
                            sp.mutez(0),
                            t1_balance,
                            )
        t2_balance = sp.contract(
                            sp.TPair(sp.TAddress, sp.TContract(sp.TNat)),
                            self.data.t2,
                            "getBalance",
                            ).open_some()
        sp.transfer(
                            (sp.self_address , sp.self_entry_point("setT2Amt")),
                            sp.mutez(0),
                            t2_balance,
                            )

    @sp.entry_point
    def switchToT1(self, params):
        sp.set_type(params, sp.TRecord(req_amt = sp.TNat))
        sp.verify(sp.sender == self.data.creator, message="Only the creator can change the proportions of tokens")
        sp.verify(self.data.clustorInited == True, message="The clustor must be inited for issuing a clustor token")

        plenty_handler = sp.contract(
                            sp.TRecord(tokenAmountIn = sp.TNat, MinimumTokenOut = sp.TNat, recipient = sp.TAddress, requiredTokenAddress = sp.TAddress, requiredTokenId = sp.TNat),
                            self.data.plentySwapAddress,
                            "Swap",
                            ).open_some()

        sp.transfer(sp.record(
                            tokenAmountIn = self.data.t2amt * self.data.clustorSupply,
                            MinimumTokenOut = params.req_amt * self.data.clustorSupply,
                            recipient = sp.self_address,
                            requiredTokenAddress = self.data.t1,
                            requiredTokenId = sp.nat(0)
                            ),
                            sp.mutez(0),
                            plenty_handler,
                            )

        t1_balance = sp.contract(
                            sp.TPair(sp.TAddress, sp.TContract(sp.TNat)),
                            self.data.t1,
                            "getBalance",
                            ).open_some()
        sp.transfer(
                            (sp.self_address , sp.self_entry_point("setT1Amt")),
                            sp.mutez(0),
                            t1_balance,
                            )
        t2_balance = sp.contract(
                            sp.TPair(sp.TAddress, sp.TContract(sp.TNat)),
                            self.data.t2,
                            "getBalance",
                            ).open_some()
        sp.transfer(
                            (sp.self_address , sp.self_entry_point("setT2Amt")),
                            sp.mutez(0),
                            t2_balance,
                            )


    @sp.entry_point
    def setClustorSupply(self, supply):
        sp.set_type(supply, sp.TNat)
        sp.verify(self.data.clustorInited == True, message="The clustor must be inited for issuing a clustor token")
        sp.verify(sp.sender == self.data.clustorToken, message="You don't have the authority to call this function")
        self.data.clustorSupply = supply

    @sp.entry_point
    def setT1Amt(self, t1Balance):
        sp.set_type(t1Balance, sp.TNat)
        sp.verify(self.data.clustorInited == True, message="The clustor must be inited for issuing a clustor token")
        sp.verify(sp.sender == self.data.t1, message="You don't have the authority to call this function")
        self.data.t1amt = t1Balance / self.data.clustorSupply

    @sp.entry_point
    def setT2Amt(self, t2Balance):
        sp.set_type(t2Balance, sp.TNat)
        sp.verify(self.data.clustorInited == True, message="The clustor must be inited for issuing a clustor token")
        sp.verify(sp.sender == self.data.t2, message="You don't have the authority to call this function")
        self.data.t2amt = t2Balance / self.data.clustorSupply  

    @sp.entry_point
    def approve_tokens(self, params):
        sp.verify(sp.sender == self.data.creator, message="Only the creator can approve the tokens")
        sp.set_type(params.token_address, sp.TAddress)
        sp.set_type(params.value, sp.TNat)
        approve_handler = sp.contract(
                            sp.TRecord(spender = sp.TAddress, value = sp.TNat).layout(("spender", "value")),
                            address=params.token_address,
                            entry_point="approve",
                            ).open_some()
        sp.transfer(sp.record(
                            spender=self.data.plentySwapAddress,
                            value=params.value
                            ),
                            sp.mutez(0),
                            approve_handler)
          

    @sp.add_test(name = "Clustor")
    def test():
        scenario = sp.test_scenario()
        scenario.h1("Clustor_Test1")
#        test_metadata = {    
#            "decimals"    : "1",              
#            "name"        : "Test",
#            "symbol"      : "TEST",
#        }
#        test_metadata2 = {    
#            "decimals"    : "1",              
#            "name"        : "Test",
#            "symbol"      : "TEST",
#        }
#        t1 = FA12.FA12(alice.address, config=FA12.FA12_config(), token_metadata = test_metadata)
#        t2 = FA12.FA12(alice.address, config=FA12.FA12_config(), token_metadata = test_metadata2) 

#        scenario += t1
#        scenario += t2

#        scenario += t1.mint(sp.record(address=bob.address, value=2000)).run(sender=alice.address)
#        scenario += t2.mint(sp.record(address=bob.address, value=2000)).run(sender=alice.address)

        c = SwitchClustorFA12(sp.address("tz1iCq9Fv4KXWRKiWft9cdDjcDv4YkcdeNTD"), sp.address("KT1SixA5zT68eFLkbhBx19aKTjz7Ds9cGsSK"), sp.address("KT19zr55VJYZ1gavnC8jPYjvhpUoAbqWJnwQ"), sp.address("KT19PC5oj39gqoRs8x69RU6RZzspM4bWpCG2") ,sp.nat(10), sp.nat(10), sp.string("Hello World"))
        scenario += c
#        scenario += c.initClustorToken().run(sender=admin.address)
#        scenario += t1.approve(spender=c.address, value=sp.nat(200)).run(sender=bob.address)
#        scenario += t2.approve(spender=c.address, value=sp.nat(200)).run(sender=bob.address)
#        scenario += c.issueToken(sp.nat(20)).run(sender=bob.address)
#        scenario += c.redeemToken(sp.nat(11)).run(sender=bob.address)
#        scenario += c.decreaseT1Amt(sp.nat(9)).run(sender=admin.address)
