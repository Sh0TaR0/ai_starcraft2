import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, SCV, SUPPLYDEPOT, MARINE, BARRACKS


class Ranto(sc2.BotAI):
    async def on_step(self, interation):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_supplydepot()
        await self.build_barracks()
        await self.build_marines()

    async def build_workers(self):
        for cc in self.units(COMMANDCENTER).ready.noqueue:
            if self.can_afford(SCV):
                await self.do(cc.train(SCV))

    async def build_supplydepot(self):
        if self.supply_left < 6 and not self.already_pending(SUPPLYDEPOT):
            cc = self.units(COMMANDCENTER).ready
            if cc.exists and self.can_afford(SUPPLYDEPOT):
                await self.build(SUPPLYDEPOT, near=cc.first)

    async def build_barracks(self):
        if self.units(SUPPLYDEPOT).ready.exists:
            sd = self.units(SUPPLYDEPOT).ready.random
            if self.can_afford(BARRACKS):
                await self.build(BARRACKS, near=sd)

    async def build_marines(self):
        for bb in self.units(BARRACKS).ready.noqueue:
            if self.can_afford(MARINE):
                await self.do(bb.train(MARINE))


run_game(maps.get("AbyssalReefLE"),
         [Bot(Race.Terran, Ranto()),
          Computer(Race.Protoss, Difficulty.Easy)], realtime=True)
