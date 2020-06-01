import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, SCV


class PythonAI(sc2.BotAI):
    async def on_step(self, interation):
        await self.distribute_workers()
        await self.build_workers()

    async def build_workers(self):
        for cc in self.units(COMMANDCENTER).ready.noqueue:
            if self.can_afford(SCV):
                await self.do(cc.train(SCV))


run_game(maps.get("AbyssalReefLE"),
         [Bot(Race.Terran, PythonAI()),
          Computer(Race.Protoss, Difficulty.Easy)], realtime=True)
