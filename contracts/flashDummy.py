
import smartpy as sp


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


#    @sp.add_test(name="flash_loan")
#    def test():
#        scenario = sp.test_scenario()
#
#        c = FlashDummy()
#        scenario += c
#        scenario += c.approve_tokens(token_address=KT1L8uYmESypf5P2Ep2QqS8L4wrB4rB29nnQ, contract_address=KT1GoM4fiPrDktzetVPbdt6gkxVhpUtNSxFq, value=sp.nat(1000))
