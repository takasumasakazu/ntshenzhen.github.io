---
title: "                      Makeblock"
date: 2025-03-21
---

ロボティクス教育のための最後のピースを埋めるMakeblock {#ロボティクス教育のための最後のピースを埋めるmakeblock .p-name}
=====================================================

::: {.section .p-summary field="subtitle"}
2016/05/27 08:00
:::

::: {.section .e-content field="body"}
::: {.section .section .section--body .section--first name="4f8d"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
### ロボティクス教育のための最後のピースを埋めるMakeblock {#b5a6 .graf .graf--h3 .graf--leading .graf--title name="b5a6"}

2016/05/27 08:00

深センのShenzhen Maker Works
Technologyは、誰でもロボティクスが学べるツール、21世紀の大人のためのレゴとして、Makeblockという製品を開発した。2012年に5人で創業した彼らは、2016年5月現在で社員200人を超える大手企業に急成長し、さらに子ども向けのロボティクス教育ツールを開発している。

![](https://cdn-images-1.medium.com/max/800/1*Ir50oCVt_y4UNT1eRS_d4Q.jpeg){.graf-image}

ロボティクス教育のための最後のピース
:::
:::
:::

::: {.section .section .section--body name="047b"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
下の画像は彼らが創業当時の[**プロモーションビデオ**](https://www.kickstarter.com/projects/1397854503/makeblock-next-generation-of-construct-platform/description){.markup--anchor
.markup--p-anchor}にあるものだ。ロボティクス、ロボット技術を学ぶためには、プログラミングと電子回路（マイクロコントローラ）に加えて、メカニクスを学ぶ必要がある。

![初期のMakeblock。](https://cdn-images-1.medium.com/max/800/1*3vAFmSfHlHWPrshiMdx9jA.jpeg){.graf-image}

Arduinoのようなマイコンを使って、ラジコンカーを作ることを考えて見よう。まず、制御するソフトウェアを書く必要がある。例えば「前」のボタンを押したときラジコンカーが前に進むためには、そのようにソフトウェアがつくられていないとならない。

電子回路がないとソフトウェアで制御できるラジコンカーはできない。前に進むためにはモーターを回す必要がある。マイクロコントローラにソフトウェアを書いたとして、電子回路を通じてモーターに決められた電力を供給しなければならない。

最後のメカニクスは前に進む仕組みのことだ。ラジコンカーならモーターにタイヤをつければ前に進むかもしれない。では、歩くとしたら？
どういう機構があれば右足と左足がかわるがわる前に出るんだろう？
モノをつかむとしたら？
関節は何個必要で、強すぎも弱すぎもしない力でモノをつかむためにはどういう機構がいるんだろう？

![Makeblockキットを構成するアルミのパーツ類。](https://cdn-images-1.medium.com/max/800/1*F857A9NEj-0bMUGCHAVIFg.jpeg){.graf-image}

Makeblockはこの機構の部分を学ぶためのツール、または楽しむためのオモチャだ。丁寧に面取りされたアルミ押し出し材で作られたパーツは堅牢で、簡単にはゆがまず、精度の高いものが作れる。等間隔に開いているネジ穴の他に中心部の溝にもネジ山が切ってあって、任意の位置に他のパーツを固定できる。基本のアルミパーツの他にジョイントやさまざまなモーターなど、機構を実現するパーツ類があり、さまざまなロボットを作ることができる。

### さまざまなキット {#66e5 .graf .graf--h3 .graf-after--p name="66e5"}

パーツをバラバラに買うこともできるが、さまざまなロボットを実現するためのキットが何種類も販売されている。

キットの中心になるマイクロコントローラはどれも共通で、Arduino
Unoと互換性がある。キットを想定通りに組みあげたら、キットごとに用意されている製品Wikiからソフトをダウンロードすれば、プログラミングができない人でもロボットを組み上げ、思い通りに動かす遊びが出来る。パーツの一つ一つは汎用のレールやギヤなので、そこでおぼえた知識は自分でロボットを思いつく発明のときに役立つ。キットの部材がアルミでできていて頑丈なこと、それぞれの部品はシンプルで何にでも使えるギヤやジョイントなどであることが応用範囲を大きく広げている。頑丈でないものでロボットキットを作ろうとすると、本体の部材があまり堅牢ではないため、多くの専用部品を使わなければならない。

![「XY Plotter Robot Kit」と「Ultimate Robot
Kit-Blue」。](https://cdn-images-1.medium.com/max/800/1*GDMfE8gnwXLck4Z-Nphd7Q.jpeg){.graf-image}

例えば、この[**「XY Plotter Robot
Kit」**](http://makeblock.com/xy-plotter-robot-kit){.markup--anchor
.markup--p-anchor}
の二次元（縦横）上で思い通りの位置に移動する仕組みと、[**「Ultimate
Robot
Kit-Blue」**](http://makeblock.com/ultimate-robot-kit-blue){.markup--anchor
.markup--p-anchor}の何かをつかむ機構をクレーンでつり下げたら、UFOキャッチャーのようなものを作ることができる。作ったことがある機構、どうやって実現できるかの仕組みが作り手に蓄積されるたびにできることが広がっていく。

### 新しいキットを生み出すハッカソン {#992e .graf .graf--h3 .graf-after--p name="992e"}

Makeblockでは、Makeblockを用いたハッカソンを頻繁に行っている。下の動画は連載の第一回で触れた[**Seeed**](https://fabcross.jp/topics/tks/20160223_tks_01.html){.markup--anchor
.markup--p-anchor}のエンジニアと一緒に行ったハッカソンで、36時間で「実用的なもの（pragmatism）」を作るのがテーマだ。テーマは「アート」「楽器」などそのたびに変わる。
:::
:::
:::

::: {.section .section .section--body name="ba88"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
36時間ハッカソン。このときは「実用的なもの（pragmatism）」がテーマ。
:::
:::
:::

::: {.section .section .section--body name="9d37"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
ハッカソンは審査員もいる真剣なものだ。僕は何度か審査員を務めたことがあるが、みな楽しみながらも本気でモノを作っていた。ギーク好みのガジェットが賞品になることも多い。Makeblockの社員の多くがエンジニアで、いつもオフィスは何かを作っている途中のMakeblockであふれている。

こうしたハッカソンから、新しいキットが派生することが多くある。この[**「Makeblock
Music Robot Kit
V2.0」**](http://makeblock.com/music-robot-kit-v2-0-with-electronics){.markup--anchor
.markup--p-anchor}はハッカソンからの派生だそうだ。

鉄筋をたたく「Makeblock Music Robot Kit V2.0」。

### 出世作の「mBot」をきっかけに、より子ども向けに {#7b69 .graf .graf--h3 .graf-after--figure name="7b69"}

Makeblockは大学でロボティクスを学んだJasen
Wangたち5人が起業した会社だ。Wangはいまも、なるべく長い時間オフィスにいて、新たなMakeblockの機構を考えている。主力製品のギヤと履帯がかみあう機構などは社長の彼が自らデザインしている。

![Makeblockオフィスを訪ねたときの筆者とWang。](https://cdn-images-1.medium.com/max/800/1*ojYsFkav_xO-endc9t0mDQ.jpeg){.graf-image}

ロボット好きが集まって成り立つ企業だけに、さらに機能を増やして何でもできる方向にキットを増やしていたが、2015年に発表した[**「mBot」**](https://fabcross.jp/news/2015/04/20150413_mbot.html){.markup--anchor
.markup--p-anchor}は、新しい方向のプロダクトだ。

もともとロボティクス教育を意図して開発されたMakeblockシリーズは、堅牢さと自由度の高さから大人がプロトタイピングツールとして使うことも多く、キットもどんどん高性能なものが出てきていたが、世界的なSTEM教育の流れの中でさらに低年齢の子供でも扱えるキットが必要になってきた。[**mBot**](http://makeblock.com/mbot-stem-educational-robot-kit-for-kids){.markup--anchor
.markup--p-anchor}はクルマとしての機能だけに絞り込み、\$74.99（約8200円）という低価格で販売しているキットだ。
:::
:::
:::

::: {.section .section .section--body name="825a"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
よりビギナー向け製品のmBot。
:::
:::
:::

::: {.section .section .section--body name="c0b6"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
ライントレースや超音波センサなどのセンサ類は豊富で、スマートフォンとBluetooth経由で接続でき、ビジュアルプログラミング言語のScratchをもとにした言語でプログラムできるなど、ソフトウェアから工夫できる部分は多いが、メカはこれまでのキットに比べてぐっとシンプルになっている。そして、このmBotはMakeblock最大のヒット商品となり、今はmBotにも派生製品がでてきた。

創業当時のMakeblockはソフトウェアを専門にするエンジニアがいなかった。当初のMakeblockも、赤外線で操作できたが、Bluetoothでスマートフォンをコントローラにしてラジコンのように動かせるのは、スマートフォンのアプリが書けるエンジニアが入社してきてからだ。

### 完全にコンシューマー向けのmBot {#b003 .graf .graf--h3 .graf-after--p name="b003"}

そして今年Makeblockは、さらにコンシューマ向けの製品として[**「CodeyBot」**](http://www.codeybot.com/){.markup--anchor
.markup--p-anchor}をリリースした。
:::
:::
:::

::: {.section .section .section--body name="9c04"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
これまでのMakeblockとはまったく見た目の違う「CodeyBot」
:::
:::
:::

::: {.section .section .section--body .section--last name="38a9"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
この5月にちょうど[**クラウドファンディング**](https://fabcross.jp/news/2016/04/20160401_codeybot.html){.markup--anchor
.markup--p-anchor}が終わったばかりのこの製品は、アルミフレームで作られているこれまでのMakeblockとは見た目がまったく違う。PCとUSBでつないでファームウェアを書き込むのではなく、タブレットやスマートホンのアプリ上でプログラミングを行う。「これはMakeblockとは違う新しい製品ラインで、よりコンシューマー向けのものだ」と、オフィスを訪ねたときに社長のWangは語った。

CodeyBotはラジコンカーのように扱えるし、タブレットから顔の部分のLEDをデザインすることもできる。MP3を再生させて踊るスピーカーとしても使える。より「オモチャ」としての魅力もあり、これまでロボットにもプログラムにも無縁だった子どもへの最初の一歩を提供することを意図している。

### 高速でプロトタイピングする姿勢が進化を後押ししている {#6243 .graf .graf--h3 .graf-after--p name="6243"}

4月に僕が彼らのオフィスを訪ねたときは、社内ハッカソンの最中で、その場で週末に再訪して審査員に加わることになった。

![社内ハッカソンの決勝。中央の箱をどれだけ自分の陣地に集めたかで勝敗が決まるロボコン的なもの。](https://cdn-images-1.medium.com/max/800/1*9PcbxxaU6Ut34Y919qj4JQ.jpeg){.graf-image}

![オフィスはいつも、Makeblockを使って何かを作る社員であふれている。床にはライントレース用の線が引かれては消える。](https://cdn-images-1.medium.com/max/800/1*RZOp0bVdaF8EG7wItrDtnA.jpeg){.graf-image}

休日にもかかわらず半数近くの社員が出社してきていて、子どもを連れてきている社員もいる。4～5人で1チームをつくり、チームごとにMakeblockを使ってロボットを作る。オフィスに転がる多くの部品や床に引かれたライントレース用のテープが、Makeblockが引き続きMakerたちの会社であることを物語る。

役員以外では初めての従業員Aliceは、いつも忙しそうに働いている。疲れていないか尋ねると、「この4年間で、アメリカにも日本にもヨーロッパにも行けたし、会社がみるみる大きくなって、自分たちの製品を使ってくれるファンにたくさん会えて、世界中に友達ができた。そういう経験はなかなかできない」と語ってくれた。

深センの市内を歩くと、Makeblockのコピー品が見つかる。深センは世界の製造業の中心であると同時に、劣化コピー品のメッカでもある。Aliceにコピー品について危惧していないか訪ねると、「Makeblockが深センに本拠を置く意味はいくつもあるけど、ここだととにかく作る、売る、試すの距離が最も短くなるのがいい。このエコシステムがあるからMakeblockはスピードを持って開発ができる。コピーする会社を見てもしょうがない。もっと速く新しい製品を作り続けることに意味がある」と一蹴された。

より家電に近いCodeyBotが、市場にどう受け入れられるかは分からない。Kickstarterは大成功しているけど、まだ子供が実際に使っている段階ではないし、Kickstarterで買っている人はたいてい大人で、自分で使うためだろう。

おそらくMakeblockは今年のMaker Faire
Tokyoにもやってくるだろう。日本でCodeyBotに触れられるのはそのときが最初になるはずだ。新しい製品ラインをぜひ体験してみてもらいたい。
:::
:::
:::
:::

By [TAKASU Masakazu/高須正和](https://medium.com/@tks){.p-author
.h-card} on [March 21, 2025](https://medium.com/p/b94f721ffaa7).

[Canonical
link](https://medium.com/@tks/20160527-b94f721ffaa7){.p-canonical}

Exported from [Medium](https://medium.com) on February 6, 2026.
