import smartpy as sp
FA12 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA1.2.py")

class FlashDummy(sp.Contract):
    def __init__(self):
        self.init()

    @sp.entry_point
    def default(self):
        pass

    @sp.entry_point
    def execute_operation(self):
        pass

    @sp.entry_point
    def approve_tokens(self, params):
        sp.set_type(params.token_address, sp.TAddress)
        sp.set_type(params.contract_address, sp.TAddress)
        sp.set_type(params.value, sp.TNat)
        approve_handler = sp.contract(
                            sp.TRecord(spender = sp.TAddress, value = sp.TNat).layout(("spender", "value")),
                            address=params.token_address,
                            entry_point="approve",
                            ).open_some()
        sp.transfer(sp.record(
                            spender=params.contract_address,
                            value=params.value
                            ),
                            sp.mutez(0),
                            approve_handler)

class ClustorOfFA12(sp.Contract):
    def __init__(
        self, 
        creator : sp.TAddress, 
        tokens : sp.TMap(sp.TAddress, sp.TNat),
        clustorName : sp.TString
        ):
        self.init(
            creator = creator,
            clustorName = clustorName,
            tokens = tokens,
            clustorInited = False,
            clustorToken = sp.address("tz1iCq9Fv4KXWRKiWft9cdDjcDv4YkcdeNTD"),
            clustorSupply = sp.nat(0)
        )

    @sp.entry_point
    def default(self):
        sp.failwith("NOT ALLOWED")

    @sp.entry_point
    def initClustorToken(self):
        sp.verify(sp.sender == self.data.creator, message="Only creator can init the clustor_token")
        sp.verify(self.data.clustorInited == False, message="The clustor token has already been inited")
        token_metadata = {    
            "decimals"    : "0",              
        }
        token = sp.create_contract(
            contract = FA12.FA12(
                admin = sp.self_address, 
                config = FA12.FA12_config(), 
                token_metadata=token_metadata)
            )
        self.data.clustorInited = True
        self.data.clustorToken = token

    @sp.entry_point
    def issueToken(self, amount : sp.TNat):
        sp.verify(self.data.clustorInited == True, message="The clustor must be inited for issuing a clustor token")
        sp.verify(amount > 0, message="Please enter a valid amount of tokens")
        token_keys = self.data.tokens.keys()
        sp.for i in token_keys:
            tokens_handler = sp.contract(
                                sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))),
                                address=i,
                                entry_point="transfer",
                                ).open_some()
            sp.transfer(sp.record(
                                from_= sp.sender,
                                to_= sp.self_address,
                                value= self.data.tokens[i] * amount
                                ),
                                sp.mutez(0),
                                tokens_handler)
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
        token_keys = self.data.tokens.keys()
        sp.for i in token_keys:
            tokens_handler = sp.contract(
                                sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))),
                                address=i,
                                entry_point="transfer",
                                ).open_some()
            sp.transfer(sp.record(
                                from_= sp.self_address,
                                to_= sp.sender,
                                value= self.data.tokens[i] * amount
                                ),
                                sp.mutez(0),
                                tokens_handler)
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
    def flashLoan(self, params):
        sp.set_type(params, sp.TRecord(amount=sp.TNat, token_address=sp.TAddress , receiver_contract=sp.TAddress))
        sp.verify(self.data.tokens.contains(params.token_address), message="There is no such token in this contract")
        sp.verify(self.data.clustorInited == True, message="This can be only executed after the clustor tokens are inited")
        sp.verify(sp.amount >= sp.mutez(1000000), message="Please send a minimum amount of tez for executing the flash loan")
        c_pool = sp.contract(
            sp.TRecord(from_=sp.TAddress, to_=sp.TAddress, value=sp.TNat).layout(("from_ as from", ("to_ as to", "value"))),
            params.token_address,
            "transfer",
        ).open_some()
        sp.transfer(
            sp.record(
                from_=sp.self_address,
                to_=params.receiver_contract,
                value=params.amount,
            ),
            sp.tez(0),
            c_pool,
        )
        c_receiver = sp.contract(
            sp.TUnit,
            params.receiver_contract,
            "execute_operation",
        ).open_some()
        sp.transfer(sp.unit, sp.tez(0), c_receiver)
        rewards = (params.amount/50)
        sp.transfer(
            sp.record(
                from_=params.receiver_contract,
                to_=sp.self_address,
                value=params.amount + rewards,
            ),
            sp.tez(0),
            c_pool,
        )
        rpu = (rewards/self.data.clustorSupply) + self.data.tokens[params.token_address]
        self.data.tokens[params.token_address] = rpu
        sp.send(sp.address("tz1iCq9Fv4KXWRKiWft9cdDjcDv4YkcdeNTD"), sp.balance)

    @sp.entry_point
    def setClustorSupply(self, supply):
        sp.set_type(supply, sp.TNat)
        sp.verify(self.data.clustorInited == True, message="The clustor must be inited for issuing a clustor token")
        sp.verify(sp.sender == self.data.clustorToken, message="You don't have the authority to call this function")
        self.data.clustorSupply = supply

    @sp.add_test(name = "Clustor")
    def test():
        scenario = sp.test_scenario()
        scenario.h1("Clustor_Test1")

        admin = sp.test_account("Administrator")
        alice = sp.address("tz1iCq9Fv4KXWRKiWft9cdDjcDv4YkcdeNTD")
        bob   = sp.test_account("Bob")

        test_metadata = {    
            "decimals"    : "4",              
            "name"        : "Jakarta BTC",
            "symbol"      : "jBTC",
        }
        test_metadata2 = {    
            "decimals"    : "3",              
            "name"        : "Jakarta SOL",
            "symbol"      : "jSOL",
        }
        test_metadata3 = {    
            "decimals"    : "1",              
            "name"        : "Test",
            "symbol"      : "TEST",
        }
        t1 = FA12.FA12(sp.address("tz1iCq9Fv4KXWRKiWft9cdDjcDv4YkcdeNTD"), config=FA12.FA12_config(), token_metadata = test_metadata)
        t2 = FA12.FA12(sp.address("tz1iCq9Fv4KXWRKiWft9cdDjcDv4YkcdeNTD"), config=FA12.FA12_config(), token_metadata = test_metadata2) 
#        t3 = FA12.FA12(alice.address, config=FA12.FA12_config(), token_metadata = test_metadata3)

        scenario += t1
        scenario += t2
#        scenario += t3

        scenario += t1.mint(sp.record(address=bob.address, value=1000)).run(sender=alice, show=False)
        scenario += t2.mint(sp.record(address=bob.address, value=1000)).run(sender=alice, show=False)
        scenario += t1.mint(sp.record(address=alice, value=1000)).run(sender=alice, show=False)
        scenario += t2.mint(sp.record(address=alice, value=10000)).run(sender=alice, show=False)
#        scenario += t3.mint(sp.record(address=bob.address, value=10)).run(sender=alice.address)

        c = ClustorOfFA12(alice, sp.map({t1.address : sp.nat(100), t2.address : sp.nat(100)}), clustorName="Test-1")
        scenario += c
        scenario += c.initClustorToken().run(sender=alice, show=False)
#        scenario.h1("Issuing the Clustor")

        scenario += t1.approve(spender=c.address, value=sp.nat(1000)).run(sender=bob.address, show=False)
        scenario += t2.approve(spender=c.address, value=sp.nat(1000)).run(sender=bob.address, show=False)
#        scenario += t3.approve(spender=c.address, value=sp.nat(10)).run(sender=bob.address)
        scenario += t1.approve(spender=c.address, value=sp.nat(1000)).run(sender=alice, show=False)
        scenario += t2.approve(spender=c.address, value=sp.nat(1000)).run(sender=alice, show=False)

        scenario += c.issueToken(sp.nat(8)).run(sender=bob.address)
        scenario += c.issueToken(sp.nat(2)).run(sender=alice)
        flash = FlashDummy()
        scenario += flash
        scenario += t1.mint(sp.record(address=flash.address, value=20)).run(sender=alice, show=False)
        scenario += t1.approve(spender=c.address, value=10000).run(sender=flash.address, show=False)
        scenario += c.flashLoan(sp.record(amount=1000, token_address=t1.address, receiver_contract=flash.address)).run(sender=admin.address, amount=sp.tez(2))
        scenario += c.redeemToken(sp.nat(2)).run(sender=bob.address)