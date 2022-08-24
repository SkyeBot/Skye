from typing import Union
import discord


async def get_mute(
    mute_role: Union[int, discord.Role], *, guild: discord.Guild
) -> Union[str, int, discord.Role]:
    if isinstance(mute_role, discord.Role):
        muted_role = mute_role.id
    else:
        muted_role = mute_role

    muted_role = guild.get_role(muted_role)

    if muted_role is None:
        muted_role = discord.utils.get(guild.roles, name="Muted")

    if not muted_role:
        muted_role = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(
                muted_role,
                speak=False,
                send_messages=False,
                read_message_history=True,
                read_messages=True,
                create_public_threads=False,
                send_messages_in_threads=False,
            )

    return muted_role
