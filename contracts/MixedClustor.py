import smartpy as sp
FA12 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA1.2.py")
FA2 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA2.py")

class MixedClustor(sp.Contract):
    def __init__(
        self, 
        creator : sp.TAddress, 
        tokens : sp.TMap(sp.TAddress, sp.TNat),
        fa2tokens : sp.TMap(sp.TAddress, sp.TPair(sp.TNat, sp.TNat)), # In the pair first element represents the token_id and the second element is the token value in each clustor.
        clustorName : sp.TString
        ):
        self.init(
            creator = creator,
            clustorName = clustorName,
            tokens = tokens,
            fa2tokens = fa2tokens,
            clustorInited = False,
            clustorToken = sp.address("tz1iCq9Fv4KXWRKiWft9cdDjcDv4YkcdeNTD"),
            lockedClustors = sp.nat(0),
            lockedBalances = sp.map(l = {}, tkey = sp.TAddress, tvalue = sp.TNat),
            lockedRewards = sp.map(l = {}, tkey = sp.TAddress, tvalue = sp.TNat)
        )

    @sp.entry_point
    def default(self):
        sp.failwith("NOT ALLOWED")

    # FA2 Tokens Transfer Function
    def TransferFATwoTokens(self, params):
        sp.set_type(params, sp.TRecord(amount=sp.TNat, tokenAddress=sp.TAddress, id=sp.TNat, repay=sp.TBool))

        sp.if params.repay == True:
            arg = [
                sp.record(
                    from_ = sp.self_address,
                    txs = [
                        sp.record(
                            to_         = sp.sender,
                            token_id    = params.id , 
                            amount      = params.amount 
                        )
                    ]
                )
            ]
            transferHandle = sp.contract(
                sp.TList(sp.TRecord(from_=sp.TAddress, txs=sp.TList(sp.TRecord(amount=sp.TNat, to_=sp.TAddress, token_id=sp.TNat).layout(("to_", ("token_id", "amount")))))), 
                params.tokenAddress,
                entry_point='transfer').open_some()
            sp.transfer(arg, sp.mutez(0), transferHandle)
        
        sp.else:
            arg = [
                sp.record(
                    from_ = sp.sender,
                    txs = [
                        sp.record(
                            to_         = sp.self_address,
                            token_id    = params.id , 
                            amount      = params.amount 
                        )
                    ]
                )
            ]
            transferHandle = sp.contract(
                sp.TList(sp.TRecord(from_=sp.TAddress, txs=sp.TList(sp.TRecord(amount=sp.TNat, to_=sp.TAddress, token_id=sp.TNat).layout(("to_", ("token_id", "amount")))))), 
                params.tokenAddress,
                entry_point='transfer').open_some()
            sp.transfer(arg, sp.mutez(0), transferHandle)

    # FA1.2 Tokens Transfer Function
    def TransferFATokens(self, params):
        sp.set_type(params, sp.TRecord(amount = sp.TNat, tokenAddress = sp.TAddress, repay = sp.TBool))

        sp.if params.repay == True :
            TransferParam = sp.record(
                from_ = sp.self_address, 
                to_ = sp.sender, 
                value = params.amount
            )
            transferHandle = sp.contract(
            sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))),
            params.tokenAddress,
            "transfer"
            ).open_some()
            sp.transfer(TransferParam, sp.mutez(0), transferHandle)

        sp.else:
            TransferParam = sp.record(
                from_ = sp.sender, 
                to_ = sp.self_address, 
                value = params.amount
            )

            transferHandle = sp.contract(
                sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))),
                params.tokenAddress,
                "transfer"
                ).open_some()
            sp.transfer(TransferParam, sp.mutez(0), transferHandle)


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
            self.TransferFATokens(sp.record(amount=self.data.tokens[i] * amount , tokenAddress=i, repay=sp.bool(False)))
        fa2_keys = self.data.fa2tokens.keys()
        sp.for j in fa2_keys:
            self.TransferFATwoTokens(sp.record(amount=sp.snd(self.data.fa2tokens[j])*amount, tokenAddress=j, id=sp.fst(self.data.fa2tokens[j]), repay=False))
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
            self.TransferFATokens(sp.record(amount=self.data.tokens[i] * amount , tokenAddress=i, repay=sp.bool(True)))
        fa2_keys = self.data.fa2tokens.keys()
        sp.for j in fa2_keys:
            self.TransferFATwoTokens(sp.record(amount=sp.snd(self.data.fa2tokens[j])*amount, tokenAddress=j, id=sp.fst(self.data.fa2tokens[j]), repay=True))
            

    @sp.add_test(name = "Clustor")
    def test():
        scenario = sp.test_scenario()
        scenario.h1("Mixed Clustor")

        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")
        bob   = sp.test_account("Bob")

        test_metadata = {    
            "decimals"    : "9",              
            "name"        : "Wrapped Tezos",
            "symbol"      : "wXTZ",
        }
        test_metadata2 = {    
            "decimals"    : "9",              
            "name"        : "Wrapped Decentraland",
            "symbol"      : "wMANA",
        }
        t1 = FA12.FA12(alice.address, config=FA12.FA12_config(), token_metadata = test_metadata)
        t2 = FA12.FA12(alice.address, config=FA12.FA12_config(), token_metadata = test_metadata2) 
        f2t1 = FA2.FA2(admin=alice.address, config=FA2.FA2_config(),metadata = sp.utils.metadata_of_url("https://example.com"))

        scenario += t1
        scenario += t2
        scenario += f2t1

        example_md = FA2.FA2.make_metadata(
        name     = "Example FA2",
        decimals = 0,
        symbol   = "DFA2" )

        scenario += t1.mint(sp.record(address=bob.address, value=10)).run(sender=alice.address)
        scenario += t2.mint(sp.record(address=bob.address, value=10)).run(sender=alice.address)
#        scenario += t1.mint(sp.record(address=alice.address, value=10)).run(sender=alice.address)
#        scenario += t2.mint(sp.record(address=alice.address, value=10)).run(sender=alice.address)
        scenario += f2t1.mint(address=bob.address, amount=10, metadata=example_md, token_id=0).run(sender=alice.address)

        c = MixedClustor(admin.address, sp.map({t1.address : sp.nat(1), t2.address : sp.nat(1)}), sp.map({f2t1.address : sp.pair(sp.nat(0), sp.nat(1))}) , clustorName="Test-1")
        scenario += c
        scenario += c.initClustorToken().run(sender=admin.address)

        scenario += t1.approve(spender=c.address, value=sp.nat(10)).run(sender=bob.address)
        scenario += t2.approve(spender=c.address, value=sp.nat(10)).run(sender=bob.address)
#        scenario += t1.approve(spender=c.address, value=sp.nat(10)).run(sender=alice.address)
#        scenario += t2.approve(spender=c.address, value=sp.nat(10)).run(sender=alice.address)
        scenario += f2t1.update_operators([sp.variant("add_operator", f2t1.operator_param.make(owner=bob.address, operator=c.address, token_id=0))]).run(sender=bob.address)

        scenario.h1("Issuing the Clustor")
        scenario += c.issueToken(sp.nat(4)).run(sender=bob.address)
        scenario += c.issueToken(sp.nat(2)).run(sender=bob.address)
        scenario += c.issueToken(sp.nat(10)).run(sender=alice.address, valid=False)
        scenario.h1("Redeeming")
        scenario += c.redeemToken(sp.nat(2)).run(sender=bob.address)
        scenario += c.redeemToken(sp.nat(1)).run(sender=alice.address, valid=False)