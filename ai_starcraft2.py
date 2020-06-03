import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, SCV, SUPPLYDEPOT


class PythonAI(sc2.BotAI):
    async def on_step(self, interation):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_supplydepots()

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


run_game(maps.get("AbyssalReefLE"),
         [Bot(Race.Terran, PythonAI()),
          Computer(Race.Protoss, Difficulty.Easy)], realtime=True)
