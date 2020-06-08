
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
import random
from sc2.constants import (
    COMMANDCENTER,
    SCV,
    SUPPLYDEPOT,
    REFINERY,
    BARRACKS,
    MARINE,

)
import cv2
import numpy as np


class PythonAI(sc2.BotAI):
    async def on_step(self, interation):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_supplydepots()
        await self.build_refinerys()
        await self.build_barracks()
        await self.build_marines()
        await self.expand()
        await self.attack()
        await self.alpha()

    async def alpha(self):
        game_data = np.zeros((
            self.game_info.map_size[1],
            self.game_info.map_size[0], 3), np.uint8)

        draw_dict = {
            COMMANDCENTER: [15, (0, 255, 0)],
            SUPPLYDEPOT: [3, (20, 235, 0)],
            SCV: [1, (55, 200, 0)],
            # ASSIMILATOR: [2, (55, 200, 0)],
            BARRACKS: [3, (200, 100, 0)],
            # CYBERNETICSCORE: [3, (150, 150, 0)],
            # STARGATE: [5, (255, 0, 0)],
            # ROBOTICSFACILITY: [5, (215, 155, 0)],
            MARINE: [3, (255, 100, 0)],
            # OBSERVER: [3, (255, 255, 255)],
        }

        for unit_type in draw_dict:
            for unit in self.units(unit_type).ready:
                pos = unit.position
                cv2.circle(game_data, (int(pos[0]), int(pos[1])),
                           draw_dict[unit_type][0], draw_dict[unit_type][1], -1)

        main_base_names = ["nexus", "supplydepot", "hatchery"]
        for enemy_building in self.known_enemy_structures:
            pos = enemy_building.position
            if enemy_building.name.lower() not in main_base_names:
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), 5, (200, 50, 212), -1)
        for enemy_building in self.known_enemy_structures:
            pos = enemy_building.position
            if enemy_building.name.lower() in main_base_names:
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), 15, (0, 0, 255), -1)

        for enemy_unit in self.known_enemy_units:
            if not enemy_unit.is_structure:
                worker_names = ["probe",
                                "scv",
                                "drone"]
                pos = enemy_unit.position
                if enemy_unit.name.lower() in worker_names:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 1, (55, 0, 155), -1)
                else:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 3, (50, 0, 215), -1)

        flipped = cv2.flip(game_data, 0)
        resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)
        cv2.imshow('Alpha', resized)
        cv2.waitKey(1)

    async def build_workers(self):
        for cc in self.units(COMMANDCENTER).ready.noqueue:
            if self.can_afford(SCV):
                await self.do(cc.train(SCV))

    async def build_supplydepots(self):
        if self.supply_left < 5 and not self.already_pending(SUPPLYDEPOT):
            ccs = self.units(COMMANDCENTER).ready
            if ccs.exists:
                if self.can_afford(SUPPLYDEPOT):
                    await self.build(SUPPLYDEPOT,
                                     near=ccs.first.position.towards(
                                         self.game_info.map_center, 8))

    async def build_refinerys(self):
        for cc in self.units(COMMANDCENTER).ready:
            gases = self.state.vespene_geyser.closer_than(10.0, cc)
            for gas in gases:
                if self.supply_used > 14 and self.can_afford(REFINERY):
                    if not self.already_pending(REFINERY):
                        if self.units(REFINERY).amount < 2:
                            worker = self.select_build_worker(gas.position)
                            await self.do(worker.build(REFINERY, gas))

    async def build_barracks(self):
        if self.units(SUPPLYDEPOT).ready:
            sd = self.units(SUPPLYDEPOT).ready.random
            if self.can_afford(BARRACKS):
                if not self.already_pending(BARRACKS):
                    await self.build(BARRACKS, near=sd)

    async def build_marines(self):
        for racks in self.units(BARRACKS).ready.noqueue:
            if self.can_afford(MARINE):
                await self.do(racks.train(MARINE))

    async def expand(self):
        if self.can_afford(COMMANDCENTER):
            await self.expand_now()

    def select_target(self):
        if self.known_enemy_structures.exists:
            return random.choice(self.known_enemy_structures).position

    async def attack(self):
        if self.units(MARINE).amount < 2:
            for marine in self.units(MARINE).idle:
                await self.do(marine.move(self.enemy_start_locations[0]))
        elif self.units(MARINE).amount > 14:
            for marine in self.units(MARINE).idle:
                await self.do(marine.attack(self.select_target()))


run_game(maps.get("AbyssalReefLE"),
         [Bot(Race.Terran, PythonAI()),
          Computer(Race.Protoss, Difficulty.Easy)], realtime=True)
