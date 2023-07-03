
# <div align="center">ArcRail instructions</div>
<div align="center"> v1.0.0 </div>


------
## 目录

* [基础属性](#属性)
    + [数值类属性](#数值属性)
    + [特殊类属性](#特殊属性)
    + [其他属性](#其他属性)
* [战斗机制](#机制)
* [效果介绍](#效果)
    + [数值类效果](#数值效果)
    + [特殊类效果](#特殊效果)
    + [其他效果](#其他效果)
* [一些说明](#说明)
* [更新日志](#更新日志)

------

## [基础属性](#属性)
### [数值类属性](#数值属性)

干员的数值类属性可以通过**detail**指令来获取，以下为这类属性的详细介绍



#### 生命上限&生命值

![max_health](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\op_info\max_health.png)

干员进入战斗时生命值会被设为生命上限，**当干员的生命值小于等于0时，干员倒地离场。**



#### 攻击力

![atk](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\op_info\atk.png)

干员的攻击力与干员**普攻**或**释放技能**时所造成的伤害息息相关，干员的攻击力越高，单次攻击对敌人所造成的伤害就越大。对于**医疗干员**，攻击力越高，单次治疗所能恢复我方干员血量越多。



#### 防御力

![def](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\op_info\def.png)

干员的防御力能够减少自身受到的**物理伤害**，干员的防御力越高，对受到的物理伤害的减少效果越强。以下为物理伤害的计算公式：

**造成的伤害 = 原伤害 * (原伤害 / (原伤害 + 2 * 目标防御力))**



#### 法术抗性

![res](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\op_info\res.png)

干员的法术抗性能够减少自身受到的**法术伤害**，干员的法术抗性越高，对受到的法术伤害的减少效果越强。以下为法术伤害的计算公式：

**造成的伤害 = 原伤害 * (100 - 目标法术抗性)**

注：法术伤害有**10%的保底伤害**，实际计算公式为：

**造成的伤害 = max(原伤害 * (100 - 目标法术抗性), 原伤害 * 10%)**



#### 速度

![speed](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\op_info\speed.png)

干员的速度决定了干员在一个回合内的行动顺序，**干员速度越高，越先行动。**



#### 暴击率

![crit_r](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\op_info\crit_r.png)

干员的暴击率决定了干员进行**普攻**或使用**攻击性技能**时的暴击概率，干员的暴击率越高，暴击概率越大。



#### 暴击伤害

![crit_d](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\op_info\crit_d.png)

干员的暴击伤害决定了干员暴击后**原伤害**的增加幅度，干员的暴击伤害越高，原伤害的增加幅度越大。

注：进行伤害计算时**先计算暴击伤害再进行防御力和法术抗性的计算。**





### [特殊属性](#特殊属性)

干员的特殊属性能从各方面反映出干员的强度，它们中的大多数也可以通过**detail**指令获取。

#### 星级

![6](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\stars\6.png)

干员的星级与干员的强度有很大的关联。一般来说，高星级的干员会比低星级的干员强度更高，也会有更多的技能，但同时也更难被获取。



#### 干员等级

![level](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\op_info\level.png)

干员等级与干员的数值类属性挂钩，干员的等级越高，干员的数值类属性大多也会得到提高。在这里，干员的等级与干员的数值类属性为**线性关系**。干员等级的提升对于干员强度的提升是巨大的，在给干员升级这方面值得投入大量的资源。

tip：输入**干员升级**指令即可给干员升级，升级需要消耗龙门币





#### 技能

![1](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\skills\1.png)![3](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\skills\3.png)![19](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\skills\19.png)

每个干员都有着特定的技能，这些技能有着不同的效果，可通过**detail**指令来了解干员各个技能的作用。

通常来说，伤害类技能会指明它的伤害类型，如果没有指明，则伤害类型取决于干员的**攻击类型**。

玩家干员的伤害类技能如**没有特别指明都是可以暴击的**。与之相反，敌方干员的伤害类技能如果**没有特别指明则不会暴击**。





#### 技能等级

与干员等级的作用相似，技能等级的提升会使技能变得更强。这主要体现在技能的伤害倍率、增幅程度、技力消耗、持续时间等方面。

tip：使用**技能升级**指令即可给技能升级，升级需要消耗龙门币



#### 干员职业

干员的职业与干员的定位相关，不同职业的干员在战斗中有着不同的效果。

##### 先锋

![先锋](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\profession\先锋.png)

先锋干员拥有**很快的速度**，能够通过普攻或技能来**回复队伍的技力点**，夺得先机。

先锋-中坚：主要通过技能来回复队伍的技力点并消耗敌人的血量。

先锋-支援：能够使用技能来回复队伍的技力点并为队友提供增益效果。

先锋-冲锋：**普攻所回复的技力点翻倍。**血量较低，但攻击力和暴击率较高，能够对敌人造成巨大的伤害。



##### 近卫

![近卫](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\profession\近卫.png)

近卫干员在战斗中主要承担输出和承伤的任务。

近卫-中坚：拥有中规中矩的数值，是队伍中的重要输出。

近卫-攻坚：血量、防御和法抗都较低，但攻击较高，能对敌人造成可观的输出。

近卫-群攻：血量和攻击略低，但能一次性**对多个敌人造成伤害**，适合清理小怪。

近卫-术战：拥有中规中矩的数值，攻击造成**法术伤害**，是队伍中的重要输出。

近卫-蓄能：血量、防御和法抗较高，但攻击力很低且普攻不造成伤害，**能够使用技能嘲讽敌人**，为团队承受伤害。



##### 重装

![重装](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\profession\重装.png)

重装干员在战斗时承担治疗和承伤的任务，**能够通过普攻嘲讽敌人**。

重装-中坚：团队的壁垒，可为团队承受大量伤害。

重装-守护：在为团队承受伤害的同时**可使用技能治疗友方干员**。

重装-驱法：在为团队承受伤害的同时**可使用技能对敌人造成可观的法术伤害**。



##### 术士

![术士](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\profession\术士.png)

术士干员拥有较高的攻击力和法术抗性，但血量和防御力较低，在队伍中做主要输出。

术士-中坚：能对敌人造成可观的法术伤害。

术士-群攻：血量很低，但**能对多个敌人造成法术伤害**。



##### 狙击

![狙击](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\profession\狙击.png)

狙击干员拥有较快的速度和暴击率，但血量和防御力较低，在队伍中做主要输出。

狙击-中坚：通过技能对单个敌人造成大量伤害。

狙击-重狙：血量很低，速度较慢且攻击**不会暴击**，但攻击力很高，**能对单个敌人造成巨额伤害**。

狙击-炮手：血量很低，但**能对多个敌人造成物理伤害**。



##### 医疗

![医疗](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\profession\医疗.png)

医疗干员能够在战斗中为友方干员恢复生命值。

医疗-中坚：**普攻恢复友方干员的生命值**。

医疗-群愈：攻击力略低，**普攻恢复多个友方干员的生命值**。



##### 辅助

![辅助](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\profession\辅助.png)

辅助干员能够在战斗中为友方干员提供增益效果或削弱敌人的力量

辅助-减速：攻击造成**法术伤害**，**能够使用技能使敌人速度减少**。

辅助-削弱：攻击造成**法术伤害**，**能够使用技能使敌人各项属性减少**。

辅助-增益：**能够使用技能使友方干员的属性提升**。



##### 特种

![特种](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\profession\特种.png)

特种干员能在战斗中起到各种各样的效果，这需要根据其职业分支来判定。

特种-处决：速度极快，攻击较高但血量较少，能率先对敌人的脆弱单位进行有力的打击。



#### 攻击类型

干员的攻击类型决定了干员进行普攻时的目标类型是友方还是敌方、目标数量以及伤害类型。

目标类型：一般来说，医疗干员的目标类型为友方，其他干员的目标类型为敌方。

目标数量：对于普攻，目标数量分为单体、群体。单体即目标本身，为1个；群体即**目标及其左右两边相邻的干员**，为1-3个。

伤害类型：伤害类型分为物理、法术和真实伤害。物理和法术伤害的计算公式见[数值类属性](#数值属性)，而真实伤害能够**无视目标的防御力和法术抗性**。





### [其他属性](#其他属性)

其他属性不能通过detail指令来获取，这类属性通常能在战斗中观察到。

#### 技力点

![player_skill_count](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\atk_info\player_skill_count.png)![enemy_skill_count](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\atk_info\enemy_skill_count.png)

干员释放大部分技能时需要消耗技力点，消耗的数量与技能的强度有一定的关系。一般来说，技能越强，所需要消耗的技力点越多。**同一个队伍的干员共用技力点**。

干员进行普攻或使用一些回复类技能可以回复技力点，而先锋中的冲锋手能够在普攻时额外恢复技力点。

tip:对于敌方干员，当**敌人数量越少、敌人星级越高**，敌人普攻时所获取到的技力点越多。



#### 行动值(暂未实现)

用于决定干员的行动次序。

目前直接使用速度决定干员的行动次序。



## [战斗机制](#机制)

使用**play**指令来进行战斗。关卡信息可通过**map**指令查看。

战斗开始前，我方和敌方都可以获得一定的技力点(通常我方获得的技力点更多)。然后**所有干员根据行动次序依次行动**。

在我方干员回合时，您可以使用**atk**指令进行普攻或**skill**指令来使用技能。

在敌方干员回合时，敌人也会进行普攻或使用技能。需要注意的是，**敌人使用技能的概率会随着敌人星级的提高而提高**。

当任意一方干员全部被击倒时，战斗结束。若玩家胜利，则会自动消耗琼脂(体力)来获取战利品。

玩家可以使用**run**指令来撤退，撤退将不会消耗琼脂。




## [效果介绍](#效果)

干员在战斗中会因为各种原因获得各个效果。这些效果可能是增益效果，也有可能是削弱效果。

当干员获得某种效果时，它将会显示在干员血条的下方。

![example](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\example.png)

其中效果图标**左下角的数字为效果的持续回合**，干员在进行普攻或使用技能时这个值会减一。当效果持续时间为0时，效果消失。对于持续时间无限的效果，左下角会显示∞。

效果图标右下角的数字为效果的层数，层数越大，该效果越强。并不是所有效果都有层数，没有层数的效果将不会显示右下角的数字。



### [数值类效果](#数值效果)

数值类效果可通过效果图标左上角的箭头来判断这是一个增益效果还是削弱效果。

![buff](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\buff.png)![debuff](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\debuff.png)

当箭头为蓝色向上的箭头时，效果为增益效果；当箭头为红色向下的箭头时，效果为削弱效果。

数值类效果大多与干员的[数值类属性](#数值属性)相关，以下仅介绍一些较为特殊的数值类效果。

#### 忍耐

#### ![11](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\11.png)

每次被攻击时自身攻击力提升(有最大层数限制)。



#### 复活

#### ![12](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\12.png)

复活后进入第二阶段。



#### 攻击类型变化

#### ![13](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\13.png)

干员攻击类型变化。



#### 恢复&损血

#### ![14](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\14.png)

每回合恢复/损失最大生命值。



#### 屏障

#### ![15](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\15.png)

防御力提升，每次受到伤害防御力提升幅度减少(层数减为0时效果消失)。



#### 愤怒

#### ![16](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\16.png)

攻击力提升，每次进行攻击时攻击力额外提升(有最大层数限制)。



#### 流血

#### ![17](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\17.png)

每回合流失当前生命值。



### [特殊类效果](#特殊效果)

特殊类效果大多没有箭头标识，以下为各个特殊类效果的说明。



#### 嘲讽

#### ![18](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\18.png)

嘲讽对象必须为选中目标**(对攻击目标为友方干员或不攻击的干员无效)**。当被嘲讽的干员进行普攻时，**只能攻击嘲讽者**。当被嘲讽的干员使用的技能中**需要以敌方单位为目标时**，也必须指定嘲讽者为目标。

tip：**当嘲讽者隐匿时，嘲讽失效**。



#### 隐匿

#### ![19](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\19.png)

效果持续时间内无法被敌方的普攻或者需要指定目标的技能选中。但依旧会受到群体攻击或全体攻击的伤害(只要不指定隐匿单位为攻击目标就行)。

tip：**当队伍中所有干员都处于隐匿状态时，隐匿失效**。



#### 不死

#### ![20](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\20.png)

效果持续时间内自身，血量不会小于1。



#### 无敌

#### ![21](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\21.png)

效果持续时间内自身免疫所有伤害。



#### 沉默

#### ![22](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\22.png)

效果持续时间内无法使用技能。



#### 眩晕/冻结

#### ![23](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\23.png)![24](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\24.png)

效果持续时间内干员无法行动(会自动跳过该干员的回合)。



#### 死战

#### ![25](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\25.png)

效果持续时间结束后该干员血量清空直接倒地。



#### 寒冷

#### ![26](D:\project\Python\nonebot\Mizuki-Bot\mizuki\plugins\ArkRail\res\effects\26.png)

速度减少。**效果持续时间内再次获得寒冷效果将会被冻结1回合**。**冻结期间受到寒冷效果将会延长冻结效果的持续时间**。



## [一些说明](#说明)

由于本游戏的战斗机制为回合制游戏，因此各个干员以及敌人的属性不能照搬明日方舟中的属性，同时一些敌人的机制也发生了改变，以下对发生了重大改变的情况进行说明。



#### 物理伤害

回合制游戏中不宜使用原版游戏中物理伤害的计算公式，我们将其修改为了：

**造成的伤害 = 原伤害 * (原伤害 / (原伤害 + 2 * 目标防御力))**



#### 敌人血量

我们对敌人的血量进行了改动，这点在领袖级敌人身上尤为明显(试想一下你在一个回合制游戏中用原版干员的属性和技能想要击倒一名血量高达好几万的敌人需要多少个回合)。



#### 游击队盾卫

游击队盾卫有着极高的防御和法抗，这在回合制游戏中是很不合理的，因此我们对其进行了改动。

现在游击队盾卫初始时会有数层持续时间无限的屏障效果，这会使其开始时的防御与原版相差无几甚至更高。但随着盾卫被不断攻击，他的防御力将会不断下降，直到屏障效果消失。当屏障消失时，盾卫的防御力就会处于一个较低的水平(不会为0哦)。



#### 爱国者-行军

爱国者行军状态下存在的问题与游击队盾卫相似，我们对其进行的改动也与游击队盾卫相似。



## [更新日志](#更新日志)

v1.0.0：编写了大致的介绍。