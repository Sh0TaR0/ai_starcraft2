import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, SCV, SUPPLYDEPOT, REFINERY, BARRACKS, MARINE


class PythonAI(sc2.BotAI):
    async def on_step(self, interation):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_supplydepots()
        await self.build_refinerys()
        await self.build_barracks()
        await self.build_marines()

    async def build_workers(self):
        for cc in self.units(COMMANDCENTER).ready.noqueue:
            if self.can_afford(SCV):
                await self.do(cc.train(SCV))

    async def build_supplydepots(self):
        if self.supply_left < 5 and not self.already_pending(SUPPLYDEPOT):
            ccs = self.units(COMMANDCENTER).ready
            if ccs.exists:
                if self.can_afford(SUPPLYDEPOT):
                    await self.build(SUPPLYDEPOT, near=ccs.first)

    async def build_refinerys(self):
        for cc in self.units(COMMANDCENTER).ready:
            gases = self.state.vespene_geyser.closer_than(10.0, cc)
            for gas in gases:
                if self.supply_used > 14 and self.can_afford(REFINERY):
                    if self.units(REFINERY).amount < 2:
                        worker = self.select_build_worker(gas.position)
                        await self.do(worker.build(REFINERY, gas))

    async def build_barracks(self):
        if self.units(SUPPLYDEPOT).ready.exists:
            sd = self.units(SUPPLYDEPOT).ready.random
            if self.can_afford(BARRACKS):
                await self.build(BARRACKS, near=sd)

    async def build_marines(self):
        for racks in self.units(BARRACKS).ready.noqueue:
            if self.can_afford(MARINE):
                await self.do(racks.train(MARINE))


run_game(maps.get("AbyssalReefLE"),
         [Bot(Race.Terran, PythonAI()),
          Computer(Race.Protoss, Difficulty.Easy)], realtime=True)
