from .operator import Operator, get_operator_list, get_enemies_list


class PlayingManager:

    def __init__(self, player_ops_list: list[Operator], map_enemies_list: list[Operator]):
        self.player_ops_list = player_ops_list
        self.map_enemies_list = map_enemies_list


async def new_instance(uid: str or int, mid: str) -> PlayingManager:
    player_ops_list: list[Operator] = await get_operator_list(uid)
    map_enemies_list: list[Operator] = await get_enemies_list(mid)
    return PlayingManager(player_ops_list, map_enemies_list)
