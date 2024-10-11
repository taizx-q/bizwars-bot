import disnake
from disnake.ext import commands

intents = disnake.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


ALLOWED_WEAPONS = {"deagle", "shotgun", "cuntgun", "m4", "м4", "дигл", "шотган", "рифла", "шот"}

MAFIA_ROLES = {
    "якз": "Yakuza Mafia",
    "мекс": "Mexican Mafia",
    "колмб": "Colombian Mafia",
    "ykz": "Yakuza Mafia",
    "mex": "Mexican Mafia",
    "clmb": "Colombian Mafia"
}

ALLOWED_CHANNEL_ID = 1292859783610765516

CLEAR_ROLE_ID = 1292843521828585478

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("Эта команда доступна только в определенном канале.")
        return

    if CLEAR_ROLE_ID not in [role.id for role in ctx.author.roles]:
        await ctx.send("У вас нет прав на использование этой команды.")
        return

    if amount <= 0:
        await ctx.send("Введите количество сообщений, которое хотите удалить, больше нуля.")
        return

    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Удалено {len(deleted)} сообщений.", delete_after=5)  

# !bizwar
@bot.command()
async def bizwar(ctx, mafia: str = None, location: str = None, duration: str = None, *, weapons: str = None):
    # check channel
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("Эта команда доступна только в определенном канале.")
        return

    # arg
    if mafia is None or location is None or duration is None or weapons is None:
        await ctx.send("Не введены аргументы, советую ознакомиться с закрепом!")
        return

    # maf
    mafia_role_name = MAFIA_ROLES.get(mafia.lower())
    if not mafia_role_name:
        await ctx.send(f"Некорректная мафия: {mafia}. Допустимые: {', '.join(MAFIA_ROLES.keys())}.")
        return

    # role_get
    role = disnake.utils.get(ctx.guild.roles, name=mafia_role_name)
    if not role:
        await ctx.send(f"Роль '{mafia_role_name}' не найдена на сервере.")
        return

    # guns check
    weapons_list = weapons.split()
    invalid_weapons = [w for w in weapons_list if w not in ALLOWED_WEAPONS]
    if invalid_weapons:
        await ctx.send(f"Некорректное оружие: {' '.join(invalid_weapons)}. Допустимые: {', '.join(ALLOWED_WEAPONS)}.")
        return

    # split guns
    weapons_str = ', '.join(weapons_list)

    # authot role get
    user_mafia_role = next((role for role in ctx.author.roles if role.name in MAFIA_ROLES.values()), None)

    # embed
    embed = disnake.Embed(
        title="Бизнес-Война",
        description=(
            f"**Забивает мафия:** {mafia_role_name}\n"
            f"**Локация:** {location}\n"
            f"**Оружия:** {weapons_str}\n"
            f"**Время стрелы:** {duration}"
        ),
        color=disnake.Color.blue()
    )
    embed.add_field(name="Выбор игрока", value="Ожидание выбора...", inline=False)

    # embed
    view = BizwarView(role)
    message = await ctx.send(
        f"{ctx.author.mention} забил стрелу: {user_mafia_role.mention if user_mafia_role else 'нет роли'} vs {role.mention}", 
        embed=embed, 
        view=view
    )
    view.message = message

# menu
class BizwarView(disnake.ui.View):
    def __init__(self, role):
        super().__init__(timeout=None)
        self.role = role
        self.message = None

    @disnake.ui.select(
        placeholder="Выберите действие",
        options=[
            disnake.SelectOption(label="Принять стрелу 3х3", description="Выберите для принятия стрелы 3х3"),
            disnake.SelectOption(label="Принять стрелу 4х4", description="Выберите для принятия стрелы 4х4"),
            disnake.SelectOption(label="Принять стрелу 5х5", description="Выберите для принятия стрелы 5х5"),
        ]
    )
    async def select_callback(self, select: disnake.ui.Select, interaction: disnake.MessageInteraction):
        # accepted role check
        if self.role not in interaction.user.roles:
            await interaction.response.send_message(
                f"У вас нет доступа к этому меню. Вам нужна роль: {self.role.mention}.",
                ephemeral=True
            )
            return

        # embed check
        if interaction.message.embeds:
            embed = interaction.message.embeds[0]
            embed.set_field_at(
                index=0,
                name="Выбор игрока",
                value=f"Игрок: {interaction.user.mention}, выбрал: {select.values[0]}",
                inline=False
            )
            await interaction.message.edit(embed=embed)

        # menu deleting
        self.clear_items()
        await interaction.message.edit(view=self)
        
        await interaction.response.send_message(f"Вы выбрали: {select.values[0]}", ephemeral=True)

# bot starts
bot.run("MTI5MDI2Nzg0MTQwODQwNTU2NA.GyDnBh.jEGvEAYSGMKI9Ha8nMPqjJy7nacW0AstM7_GcQ")
