import smartpy as sp
FA12 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA1.2.py")
FA2 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA2.py")
FLASH = sp.io.import_stored_contract("flashDummy")

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


    @sp.entry_point
    def lockClustors(self, amount):
        sp.set_type(amount, sp.TNat)
        sp.verify(self.data.clustorInited == True, message="The clustor tokens must be initialised before locking in the function")
        sp.verify(amount > 0, message="The locking amount cannot be zero")

        self.TransferFATokens(sp.record(amount=amount, tokenAddress=self.data.clustorToken, repay=sp.bool(False)))

        sp.if self.data.lockedBalances.contains(sp.sender):
            self.data.lockedBalances[sp.sender] += amount
        sp.else:
            self.data.lockedBalances[sp.sender] = amount

        sp.if ~ self.data.lockedRewards.contains(sp.sender):
            self.data.lockedRewards[sp.sender] = sp.nat(0)

        clustor_balance = sp.contract(sp.TPair(sp.TAddress, sp.TContract(sp.TNat)), self.data.clustorToken, "getBalance").open_some()
        sp.transfer((sp.self_address , sp.self_entry_point("updateLockedClustors")),sp.tez(0),clustor_balance)

    @sp.entry_point
    def unlockClustors(self, amount):
        sp.set_type(amount, sp.TNat)
        sp.verify(self.data.clustorInited == True, message="This can be only executed after the clustor tokens are inited")
        sp.verify(amount > 0, message="The unlocking amount cannot be zero")
        sp.verify(self.data.lockedBalances.contains(sp.sender), message="You don't have any tokens locked to unlock")

        self.TransferFATokens(sp.record(amount=amount, tokenAddress=self.data.clustorToken, repay=sp.bool(True)))

        sp.if self.data.lockedBalances[sp.sender] - amount == 0:
            del self.data.lockedBalances[sp.sender]
            sp.if self.data.lockedRewards[sp.sender] != 0:
                sp.send(sp.sender, sp.utils.nat_to_mutez(self.data.lockedRewards[sp.sender]))
            del self.data.lockedRewards[sp.sender]
        sp.else:
            claimable = (self.data.lockedRewards[sp.sender] / self.data.lockedBalances[sp.sender]) * amount
            sp.if claimable != 0:
                sp.send(sp.sender, sp.utils.nat_to_mutez(claimable))
            self.data.lockedRewards[sp.sender] = sp.as_nat(self.data.lockedRewards[sp.sender] - claimable)
            self.data.lockedBalances[sp.sender] = sp.as_nat(self.data.lockedBalances[sp.sender] - amount)
        clustor_balance = sp.contract(sp.TPair(sp.TAddress, sp.TContract(sp.TNat)), self.data.clustorToken, "getBalance").open_some()
        sp.transfer((sp.self_address , sp.self_entry_point("updateLockedClustors")),sp.tez(0),clustor_balance)

    @sp.entry_point
    def updateLockedClustors(self, amt):
        sp.set_type(amt, sp.TNat)
        sp.verify(sp.sender == self.data.clustorToken, message="This can be only called by the Clustor Token contract")
        sp.verify(self.data.clustorInited == True, message="This can be only executed after the clustor tokens are inited")
        self.data.lockedClustors = amt


    @sp.entry_point
    def flashLoan(self, params):
        sp.set_type(params, sp.TRecord(amount=sp.TNat, token_address=sp.TAddress , receiver_contract=sp.TAddress, fa2=sp.TBool, token_id=sp.TNat))
        sp.verify(self.data.tokens.contains(params.token_address) | self.data.fa2tokens.contains(params.token_address), message="There is no such token in this contract")
        sp.verify(self.data.clustorInited == True, message="This can be only executed after the clustor tokens are inited")
        sp.verify(sp.amount >= sp.mutez(1000000), message="Please send a minimum amount of tez for executing the flash loan")

        sp.if params.fa2 == True:
            sp.verify(params.amount < sp.snd(self.data.fa2tokens[params.token_address]) * self.data.lockedClustors, message="The contract doesn't have enough token balance")
            arg = [
                sp.record(
                    from_ = sp.self_address,
                    txs = [
                        sp.record(
                            to_         = params.receiver_contract,
                            token_id    = params.token_id , 
                            amount      = params.amount 
                        )
                    ]
                )
            ]
            transferHandle = sp.contract(
                sp.TList(sp.TRecord(from_=sp.TAddress, txs=sp.TList(sp.TRecord(amount=sp.TNat, to_=sp.TAddress, token_id=sp.TNat).layout(("to_", ("token_id", "amount")))))), 
                params.token_address,
                entry_point='transfer').open_some()
            sp.transfer(arg, sp.mutez(0), transferHandle)
            c_receiver = sp.contract(
                sp.TUnit,
                params.receiver_contract,
                "execute_operation",
            ).open_some()
            sp.transfer(sp.unit, sp.tez(0), c_receiver)
            arg = [
                sp.record(
                    from_ = params.receiver_contract,
                    txs = [
                        sp.record(
                            to_         = sp.self_address,
                            token_id    = params.token_id, 
                            amount      = params.amount 
                        )
                    ]
                )
            ]
            transferHandle = sp.contract(
                sp.TList(sp.TRecord(from_=sp.TAddress, txs=sp.TList(sp.TRecord(amount=sp.TNat, to_=sp.TAddress, token_id=sp.TNat).layout(("to_", ("token_id", "amount")))))), 
                params.token_address,
                entry_point='transfer').open_some()
            sp.transfer(arg, sp.mutez(0), transferHandle)
        sp.else:
            sp.verify(params.amount < self.data.tokens[params.token_address] * self.data.lockedClustors, message="The contract doesn't have enough token balance")
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
            sp.transfer(
                sp.record(
                    from_=params.receiver_contract,
                    to_=sp.self_address,
                    value=params.amount,
                ),
                sp.tez(0),
                c_pool,
            )
        rewards = sp.utils.mutez_to_nat(sp.amount) / self.data.lockedClustors
        reward_keys = self.data.lockedBalances.keys()
        sp.for i in reward_keys:
            self.data.lockedRewards[i] += rewards * self.data.lockedBalances[i]


    """
        Testing Scenarios 
    """


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
        scenario += t1.mint(sp.record(address=alice.address, value=10)).run(sender=alice.address)
        scenario += t2.mint(sp.record(address=alice.address, value=10)).run(sender=alice.address)
        scenario += f2t1.mint(address=bob.address, amount=10, metadata=example_md, token_id=0).run(sender=alice.address)
        scenario += f2t1.mint(address=alice.address, amount=10, metadata=example_md, token_id=0).run(sender=alice.address)

        c = MixedClustor(admin.address, sp.map({t1.address : sp.nat(1), t2.address : sp.nat(1)}), sp.map({f2t1.address : sp.pair(sp.nat(0), sp.nat(1))}) , clustorName="Test-1")
        scenario += c
        scenario += c.initClustorToken().run(sender=admin.address)

        scenario += t1.approve(spender=c.address, value=sp.nat(10)).run(sender=bob.address)
        scenario += t2.approve(spender=c.address, value=sp.nat(10)).run(sender=bob.address)
        scenario += t1.approve(spender=c.address, value=sp.nat(10)).run(sender=alice.address)
        scenario += t2.approve(spender=c.address, value=sp.nat(10)).run(sender=alice.address)
        scenario += f2t1.update_operators([sp.variant("add_operator", f2t1.operator_param.make(owner=bob.address, operator=c.address, token_id=0))]).run(sender=bob.address)
        scenario += f2t1.update_operators([sp.variant("add_operator", f2t1.operator_param.make(owner=alice.address, operator=c.address, token_id=0))]).run(sender=alice.address)

        scenario.h1("Issuing")
        scenario += c.issueToken(sp.nat(4)).run(sender=bob.address)
        scenario += c.issueToken(sp.nat(2)).run(sender=alice.address)
        scenario += c.issueToken(sp.nat(10)).run(sender=alice.address, valid=False)
        scenario.h1("Redeeming")
        scenario += c.redeemToken(sp.nat(1)).run(sender=bob.address)
        scenario += c.redeemToken(sp.nat(8)).run(sender=alice.address, valid=False)
        scenario.h1("Locking & Unlocking")
        scenario += c.lockClustors(sp.nat(10)).run(sender=alice.address, valid=False)
        scenario += c.unlockClustors(sp.nat(1)).run(sender=bob.address, valid=False)
        scenario += c.lockClustors(sp.nat(3)).run(sender=bob.address)
        scenario += c.lockClustors(sp.nat(2)).run(sender=alice.address)
        scenario.h1("Flash Testing")
        flash = FLASH.FlashDummy()
        scenario += flash
        scenario += f2t1.update_operators([sp.variant("add_operator", f2t1.operator_param.make(owner=flash.address, operator=c.address, token_id=0))]).run(sender=flash.address)
        scenario += c.flashLoan(sp.record(amount=1, token_address=f2t1.address, receiver_contract=flash.address, token_id=0, fa2=True)).run(sender=admin.address, amount=sp.tez(1))
        scenario += t1.approve(spender=c.address, value=10).run(sender=flash.address)
        scenario += c.flashLoan(sp.record(amount=10, token_address=t1.address, receiver_contract=flash.address, token_id=0, fa2=False)).run(sender=admin.address, amount=sp.tez(1), valid=False)
        scenario += c.flashLoan(sp.record(amount=2, token_address=t1.address, receiver_contract=flash.address, token_id=0, fa2=False)).run(sender=admin.address, amount=sp.tez(1))
        scenario += c.unlockClustors(2).run(sender=alice.address)
        scenario += c.unlockClustors(sp.nat(1)).run(sender=bob.address)

