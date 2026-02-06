---
title: "M5Stack         Stamp Fly       "
date: 2025-03-27
---

M5Stackのドローンキット「Stamp Fly」製品化への道 {#m5stackのドローンキットstamp-fly製品化への道 .p-name}
================================================

::: {.section .p-summary field="subtitle"}
2024/11/19 06:30
:::

::: {.section .e-content field="body"}
::: {.section .section .section--body .section--first name="2c0f"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
### M5Stackのドローンキット「Stamp Fly」製品化への道 {#98c6 .graf .graf--h3 .graf--leading .graf--title name="98c6"}

2024/11/19 06:30

![](https://cdn-images-1.medium.com/max/800/1*pKwqRRiG82bJZw5UofPgAw.png){.graf-image}

日本でも人気の「M5Stack」シリーズは、画面やボタンなどが一体型になっていて、手軽に使えるマイコンボードだ。

2020年に開発元のM5Stackが自由にプログラムできるドローンキットを開発したが、同社だけではうまくいかずにプロジェクトは失敗になりかけていた。そこに金沢工業大学（以下、金沢工大）で飛行制御を教える[**伊藤恒平**](https://twitter.com/kouhei_kanazawa){.markup--anchor
.markup--p-anchor}教授、ドローン愛好家でハードウェア分解／改造などにも親しんでいる[**GOROman**](https://twitter.com/GOROman){.markup--anchor
.markup--p-anchor}氏、[**Necobut**](https://twitter.com/necobut){.markup--anchor
.markup--p-anchor}氏など、日本のエンジニアたちが共同開発に参加し、急ピッチで開発が再開した。ここまでの経緯はfabcrossで[**前回のレポート**](https://fabcross.jp/topics/tks/20230110_m5stack_drone.html){.markup--anchor
.markup--p-anchor}で報告したとおりだ。
:::
:::
:::

::: {.section .section .section--body .section--last name="142f"}
::: {.section-divider}

------------------------------------------------------------------------
:::

::: {.section-content}
::: {.section-inner .sectionLayout--insetColumn}
[**日本で飛ばせるドローンを作ろう！
M5StackのAtomFlyプロジェクト｜fabcross**](https://fabcross.jp/topics/tks/20230110_m5stack_drone.html){.markup--anchor
.markup--p-anchor}

ただ、前回レポートしたのは2023年の1月。それから実際の製品[**「M5Stamp
Fly」**](https://www.switch-science.com/products/9818){.markup--anchor
.markup--p-anchor}と[**「M5Atom
Joystick」**](https://www.switch-science.com/products/9819){.markup--anchor
.markup--p-anchor}が2024年8月に販売されるまでは1年以上の月日が経過した。しかも販売された製品は、前回のレポートで紹介したAtom
Flyとは別製品となった。

Stamp
Flyは初期ロットの完売以後、オープンソースのドローン入門キットとして、多くのバックオーダーを得る人気商品となった。あまり人気が出ず、発売すぐにお蔵入りとなったAtom
Flyと、大人気となったStamp Flyの間では、どういう変更が行われたのか？
2024年10月26日に行われたオンラインイベント[**「\#M5Stack \#Stampfly
開発ストーリーと今後の可能性」**](https://youtu.be/qkmUqAKEcUc){.markup--anchor
.markup--p-anchor}にて公開された、製品開発の過程をレポートする。

![製品となったStamp Fly。Atom
Fly改善プロジェクトが始まってから2年近くが経過し、2024年8月に販売された。](https://cdn-images-1.medium.com/max/800/1*qvk7In8E8eSRxlYLwvdwUw.png){.graf-image}

### 大規模改修を行っても、販売に至らなかった次世代Atom Fly {#63f1 .graf .graf--h3 .graf-after--figure name="63f1"}

旧製品Atom
Flyの改善に日本のユーザーたち、特に飛行制御の専門家である金沢工大の伊藤恒平教授が協力するようになったことで、開発は急ピッチで進んだ。実際に飛行させるワークショップなども行えるようになった。

2022年末～2023年初頭のX（旧twitter）のスレッドには、

-   [飛行制御のためのファームウェア適用]{#b4b2}
-   [Atom Fly
    のハードウェア改修、センサーの追加やPCBで構成されたボディの設計改善]{#18f9}

など、毎週のように新しいファームウェアがテストされ、深圳にあるM5Stackからも頻繁にバージョンアップした試作品が届いている様子がうかがえる。

> [](https://twitter.com/kouhei_kanazawa/status/1601734123160473601?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1601735702005575681%7Ctwgr%5E27899e29e67d442020b25723802f4ca568b4e414%7Ctwcon%5Es2_&ref_url=https%3A%2F%2Ffabcross.jp%2Ftopics%2Ftks%2F20241119_m5stack_stampfly.html)

しかし改善の結果、飛行テストが行えるようになったことで、旧製品Atom
Flyの根本的な欠陥が明らかになった。PCB基板で作られている筐体が壊れやすく、初心者が気軽に実験できるような強度が実現しないのだ。

PCBの設計を変える、3Dプリンターで作ったカバーを付けるなどの対策をいくつも講じたが、安心してテストできるような強度にはならない。カーボンなどの高額な部材を使うと販売価格も上がってしまう。

また、安定した飛行には高度制御に使うToF（Time of
Flight）距離センサーや気圧センサー、同じ地点でのホバリングを可能にするオプティカルフローセンサーなどの複数のセンサーを追加した方が良いが、Atom
Flyで採用していたマイコンキットM5Stack [**「ATOM
Lite」**](https://www.switch-science.com/products/6262){.markup--anchor
.markup--p-anchor}ではピンの数が足りず、追加できない。

> [](https://twitter.com/GOROman/status/1660648937827565571?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1660649352585523210%7Ctwgr%5E27899e29e67d442020b25723802f4ca568b4e414%7Ctwcon%5Es2_&ref_url=https%3A%2F%2Ffabcross.jp%2Ftopics%2Ftks%2F20241119_m5stack_stampfly.html)

このままAtom Flyを改良してAtom
Fly2として製品化する方向だと、製品化へのゴールははるかに遠いように思われた。

### 2023年5月 筐体とMCUを変更し、別製品「Stamp Fly」が誕生 {#8f35 .graf .graf--h3 .graf-after--p name="8f35"}

![Atom
Flyにガードを付けるなどさまざまな改善を行った（左）が、市販のトイドローン筐体に合わせてPCB基板を開発する（右）ことで耐久性、飛行安定性が大幅に改善（[**伊藤教授のスライド**](https://www.docswell.com/s/Kouhei_Ito/K228YN-2024-10-27-074715){.markup--anchor
.markup--figure-anchor}より）。](https://cdn-images-1.medium.com/max/800/1*CXTtIACUsXKWr25y9ylDuQ.png){.graf-image}

開発メンバーの1人である
GOROman氏が、手持ちのマイクロドローンフレームにAtomflyの制御部分を無理やり組み込んだプロトタイプを作ったことが大きなヒントになった。深圳では多くのメーカーがマイクロドローンを開発しているため、65mm／75mmといったサイズのドローンフレームならば、デファクトスタンダード化された樹脂の強靭なフレームを市場で調達できる。

また、M5Stackのマイコンキット[**「M5Stamp
S3」**](https://www.switch-science.com/products/8777){.markup--anchor
.markup--p-anchor}が2023年2月に発売されたことも後押しになった。Atom
Flyで使っていたAtom
Lite（12g）よりはるかに軽く（3.2g）、性能の高いESP32-S3を搭載していた。かつ、より未使用ピンが多いことで、センサー類の追加に対応できる。

![M5StampS3
製品に組み込むことを意図した、小さく拡張性の高いモデル。](https://cdn-images-1.medium.com/max/800/1*mooRRXtyXLfX2HJIr8FkPQ.png){.graf-image}

新しいフレームに合わせてPCBを設計するため、MCUも変更してM5Stamp
S3を採用した。さらに伊藤教授のアドバイスを受けて、センサー類を再度精査することになった。Atom
Flyの改良版でなく、新しいモデルとしてのStamp Flyの誕生である。

### 深圳のドローン企業 BETAFPVとの協業により、バッテリー／筐体が改善 {#a7eb .graf .graf--h3 .graf-after--p name="a7eb"}

筐体の購入や、それに合わせたモーター、ローターなどの購入では、筆者ほか日本のドローン愛好家がかねてから馴染みの深圳のドローン企業BETAFPVと協業できた。筐体サイズを同社が使用している65mmサイズのドローンフレームに合わせ、バッテリーも同社のもの（BT2.0コネクターの「LAVA
1S」）を採用することになった。

同社のバッテリーはこのサイズのドローン用に最適化されていて、容量が下がっても高い電圧を保てる。これにより、飛行時間が延びて4分の飛行が可能になった。BETAFPVも、競合製品になりかねない同サイズのドローン開発に対して、バッテリーなどの卸販売、モーターなどの取引先紹介に嬉々として協力してくれた。こうした柔軟なサプライチェーン構築は、深圳の特色といえる。

![2023年8月、M5StackのCEO
Jimmy（左から２人目）と共にBETAFPVで打ち合わせしたことにより、さまざまな問題が一気に解消された。](https://cdn-images-1.medium.com/max/800/1*tpjoEhsqU023_TjhhIv3lA.png){.graf-image}

### コントローラーを再設計 Atom Joystick {#964f .graf .graf--h3 .graf-after--figure name="964f"}

Stamp
FlyがESP32-S3を使ったことから、コントローラーもESP32-S3を採用した[**ATOMS3**](https://www.switch-science.com/products/8670){.markup--anchor
.markup--p-anchor}を前提にM5ATOM Joystickとして再設計された。

M5ATOM Joystickは、USB Type-C端子からの給電だ。Stamp
Flyで使用するバッテリーを充電する機能を備えたことで、本体とは別に充電器を用意する必要がなくなった。「この充電機構や、コントローラーにも同じバッテリーを採用して充電器を不要にしたことは、M5Stack
CEOで設計者であるJimmyのアイデア賞ですね」と伊藤教授も称賛する。

![コントローラーがそのままドローンバッテリーの充電器になるM5ATOM
Joystick。操作も通常のコントローラーと同じ、左右2本のジョイスティックになった。](https://cdn-images-1.medium.com/max/800/1*PBWhJnJraNNcJRhHtFatBg.png){.graf-image}

### マルチコプター制御の入門キットとして {#ae2a .graf .graf--h3 .graf-after--figure name="ae2a"}

ハードウェアとして完成度が上がり、使いやすくなったことで、Stamp
Flyはマルチコプター制御の入門キットとして広く受け入れられる可能性を秘めている。

一般的なラジコンカーは、モーターの正逆転による前進／後退とサーボモーターによるステアリングの操作がコントローラーと直接対応している。一方、ドローンは、各ローターの回転数を調整することで上昇や前進などの挙動を行う。ドローンではコントローラー操作とそれぞれのモーターは直接対応しておらず、フライトコントローラーがドローンに搭載されたセンサー値を計算し、モーターの出力をコントロールしつづけるフィードバックループを絶え間なく続けることで操作する。

![マルチコプターは、センサーの値から角度や高さを推定しつづけ、プロポ（送信機）からの入力値をモーターのPID制御に変えることで飛行できる（伊藤教授のスライドより）。](https://cdn-images-1.medium.com/max/800/1*i9WyIPRTJus4XKXc-90x2A.png){.graf-image}

伊藤教授はStamp
Flyを教材に、学生にマルチコプターの制御を20コマ（1日4コマ×5日）の集中講義で行う授業をすでに行っている。

### オープンなハードウェアによる、別のファームウェアの適用／さらには教材化 {#2a94 .graf .graf--h3 .graf-after--p name="2a94"}

ファームウェアが公開され、マイコンへの書き込み手段が整備されたオープンなドローンキットは珍しく、発売後には[**ArduPilot**](https://ardupilot.org/){.markup--anchor
.markup--p-anchor}など別のファームウェアを書き込んだ事例も見られた。Stamp
Flyの登場は、安価なハードウェアの誕生でさまざまなドローン制御ソフトウェアのコミュニティを勢いづかせている。

また2024年10月には、金沢市の企業であるFAP
factoryが伊藤教授と連携して、広く使われている教育用マイコン（micro:bitなど）とStamp
Flyを連携させるプロジェクト[**「StampFly
Edu」**](https://www.dreamnews.jp/press/0000307264/){.markup--anchor
.markup--p-anchor}を公開した。micro:bitの対象年齢である12歳以下の年齢層も、コンピューター制御でドローンを動かすことを可能にするプロジェクトだ。

製造トラブルにより品不足が続いていたStamp FlyやM5ATOM
Joystickも生産が再開され、日本での販売も再開された。M5Stackでも追加生産を続けているので、年内にはさまざまな電子部品ショップに並ぶ姿も見られる見込みだ。

開発に多くの日本人エンジニアが関わったことにより、Stamp
Flyを中心にした産業のエコシステムが日本でできつつある。こうした成果が世界に向けて広がっていくのが、とても楽しみなプロジェクトになっている。
:::
:::
:::
:::

By [TAKASU Masakazu/高須正和](https://medium.com/@tks){.p-author
.h-card} on [March 27, 2025](https://medium.com/p/5fc792fb431c).

[Canonical
link](https://medium.com/@tks/20241119-5fc792fb431c){.p-canonical}

Exported from [Medium](https://medium.com) on February 6, 2026.
