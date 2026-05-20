# Source Download Status
Updated: 2026-02-28

## Sources (15 retained after review)

4 sources removed after content review:
- ~~09_静岡県~~ — Branding materials only (logos, mascot, LINE stamps). Zero term pairs.
- ~~11_宇都宮市~~ — 8-page policy overview. No structured term list.
- ~~15_島根県~~ — 6-page pamphlet. ~15 example pairs, too few to justify.
- ~~16_北海道~~ — Tourism-focused. Wrong domain for municipal 行政 use case.

### Tier 1: Structured term lists (prioritize for extraction)

| # | Source | Files | Est. pairs | Notes |
|---|--------|-------|------------|-------|
| 01 | 出入国在留管理庁・文化庁 ガイドライン + 別冊書き換え例 | `01_…/ガイドライン本体.pdf` (2.1MB), `01_…/別冊_書き換え例.pdf` (332KB, 18pp) | TBD | National standard. 別冊 is the key term list. |
| 02 | 出入国在留管理庁 やさしい日本語書き換えツール | `02_…/書き換えツール_語彙データ.json`, `.csv` (925 entries) | **925** ✅ | Extracted from embedded JS. Ready to use. |
| 03 | 弘前大学 災害基礎語彙集成 | `03_…/地震災害基礎語彙100.csv`, `03_…/大雨_洪水_土砂災害基礎語彙100.csv` | **200** ✅ | Both CSVs extracted and ready. |
| 07 | 福岡市「使ってみよう やさしい日本語」+ 用語集 | `07_…/使ってみよう_やさしい日本語.pdf` (3.4MB), `07_…/用語集.pdf` (1.5MB) | TBD | Separate 用語集 PDF — structured term pairs. |
| 08 | 三重県 やさしい日本語ガイドライン (2025-01) | `08_…/やさしい日本語ガイドライン.pdf` (2.9MB) | ~60 | 言い換えリスト (p.19-20): 緊急・災害, 健康・医療, 生活・仕事, 子育て・教育. |
| 12 | 横浜市 やさしい日本語で伝える + 語彙集 + 例文集 | `12_…/ガイドライン.pdf`, `語彙集.pdf`, `語彙集.xlsx` (561 terms), `例文集.pdf` | **561** | Excel has structured term pairs. Highest extraction value after ISA. |
| 13 | 大阪府「やさしい日本語を使いましょう」 | `13_…/やさしい日本語を使いましょう_全ページ.pdf` (6.6MB) | TBD | 用語集 (p.22-31) + 6 lesson exercises across domains. |
| 14 | 愛知県 やさしい日本語の手引き | `14_…/やさしい日本語の手引き.pdf` (4.7MB, 32pp) | ~150 | 用語集・文例集 (p.21-26): お仕事編 (役所, 学校, 病院, 警察, 交通, 観光, 商店, 緊急) + 生活編 (自己紹介, 家族, 住居, 交通, 自治会, 食べ物). Includes 言い換えポイント column. |
| 19 | 入間市 やさしいにほんご + いいかえひょう | `19_…/やさしいにほんごについて.pdf`, `いいかえひょう.pdf` (5pp), `パンフレット.pdf` | **183** | Broad 行政 coverage. Cleanly structured term pairs. |

### Tier 2: Sentence examples / scattered pairs

| # | Source | Files | Content | Notes |
|---|--------|-------|---------|-------|
| 04 | 鳥取県 防災ハンドブック | `04_…/防災ハンドブック.pdf` (9.0MB, 28pp) | Sentence examples | Already in やさしい日本語. Covers 地震, 台風/大雨, 大雪. |
| 05 | 川崎市 やさしい日本語ガイドライン 第2版 (2023) | `05_…/やさしい日本語ガイドライン第2版.pdf` (3.4MB, 24pp) | ~30 scattered pairs | Methodology guide with inline examples (敬語→普通語, 漢語→和語, 漢字→ひらがな). |
| 06 | 札幌市 やさしい日本語ガイドライン (2025-02) | `06_…/やさしい日本語ガイドライン.pdf` (1.3MB) | ~20 inline pairs | Methodology + survey data. Some term rewrites in ポイント3 ことば section. |
| 10 | 大阪市 防災やさしい日本語 | `10_…/地震が来たとき.pdf` (16pp), `10_…/台風が来たとき.pdf` (18pp) | Sentence examples | Full documents already in やさしい日本語 for 2 disaster scenarios. |
| 17 | 岡山県 やさしい日本語の手引き | `17_…/やさしい日本語の手引き.pdf` (5.6MB) | Conversation rewrites + 言い換え | 困ったときに使うことば, 言い換え section (p.17), 岡山弁→やさしい日本語 (p.20). |
| 18 | 京都市 分かりやすく伝えるための手引き | `18_…/分かりやすく伝えるための手引き.pdf` (2.3MB) | 書き換えリスト集 (p.11+) | Structured rewrite list + practice problems. |

## Source URLs

| # | URL |
|---|-----|
| 01a | https://www.bunka.go.jp/seisaku/kokugo_nihongo/kyoiku/pdf/92484001_01.pdf |
| 01b | https://www.bunka.go.jp/seisaku/kokugo_nihongo/kyoiku/pdf/92484001_02.pdf |
| 02 | https://www.moj.go.jp/isa/support/portal/plainjapanese_kakikaerei.html (data extracted from embedded JS) |
| 03a | Wayback Machine: `web.archive.org/web/20191127/http://human.cc.hirosaki-u.ac.jp/kokugo/EJ100go-top.html` |
| 03b | https://www.city.fukuyama.hiroshima.jp/uploaded/attachment/199054.pdf (mirror) |
| 03c | https://www.fdma.go.jp/singi_kento/kento/items/kento207_20_sankou5-6.pdf |
| 04 | http://www.torisakyu.or.jp/user/filer_public/35/42/35421010-5ff4-469b-8d79-8af7c8964798/bosaihandbook2023_single_high_202411_light.pdf |
| 05 | https://www.city.kawasaki.jp/250/cmsfiles/contents/0000127/127357/pdf1_yasasihi2023.pdf |
| 06 | https://www.city.sapporo.jp/kokusai/documents/yasasiinihongo-guideline202502.pdf |
| 07a | https://www.city.fukuoka.lg.jp/soki/kokusai/shisei/japanese/documents/sassi.pdf |
| 07b | https://www.city.fukuoka.lg.jp/soki/kokusai/shisei/japanese/documents/yougosyuu.pdf |
| 08 | https://www.pref.mie.lg.jp/common/content/001173183.pdf |
| 10a | https://www.city.osaka.lg.jp/kikikanrishitsu/cmsfiles/contents/0000350/350870/22.02.22jishin_kitatoki.pdf |
| 10b | https://www.city.osaka.lg.jp/kikikanrishitsu/cmsfiles/contents/0000350/350870/22.02.22taihu_kitatoki.pdf |
| 12a | https://www.city.yokohama.lg.jp/lang/residents/ja/kurashi/kyodo-manabi/kokusai/yasasiinihongo/yasanichi-guideline.files/0003_20240405.pdf |
| 12b | https://www.city.yokohama.lg.jp/lang/residents/ja/kurashi/kyodo-manabi/kokusai/yasasiinihongo/yasanichi-guideline.files/0004_20240405.pdf |
| 12c | https://www.city.yokohama.lg.jp/lang/residents/ja/kurashi/kyodo-manabi/kokusai/yasasiinihongo/yasanichi-guideline.files/0005_20240405.pdf |
| 12d | https://www.city.yokohama.lg.jp/lang/residents/ja/kurashi/kyodo-manabi/kokusai/yasasiinihongo/yasanichi-guideline.files/0006_20240405.xlsx |
| 13 | https://www.pref.osaka.lg.jp/attach/1aborni/00000000/yasasiinihongo.pdf |
| 14 | https://www.pref.aichi.jp/uploaded/attachment/431191.pdf |
| 17 | https://www.pref.okayama.jp/uploaded/life/926338_9546498_misc.pdf |
| 18 | https://www.city.kyoto.lg.jp/sogo/cmsfiles/contents/0000302/302389/tebiki.pdf |
| 19a | https://www.city.iruma.saitama.jp/material/files/group/15/yasanichinituite.pdf |
| 19b | https://www.city.iruma.saitama.jp/material/files/group/15/yasanichiiikae.pdf |
| 19c | https://www.city.iruma.saitama.jp/material/files/group/15/yasanichipanf.pdf |
