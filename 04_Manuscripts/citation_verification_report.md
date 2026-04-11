# 引用元文献と引用箇所の一致検証レポート（厳格判定）

## 判定基準
- 本文の主張・文脈と、引用文献の**主題・アウトカム・地域**が一致しているかを厳しく確認した。
- 糖尿病を主アウトカムとする論文において、心血管疾患のみの文献を糖尿病の根拠として用いている場合は**不一致**とした。

---

## 不一致と判定した箇所

### 1. Ref 9) Yanagida et al. — **心血管疾患の文献を糖尿病文脈で引用**

**文献の内容**: "Air Pollution and **Cardiovascular Diseases** in Japan: No More An Enigma"（動脈硬化血栓誌 2021）. 主題は**心血管疾患**であり、糖尿病は主アウトカムではない。

**引用箇所と問題点**:
- 113行目: 「large, easily detectable effects of PM2.5 on these aggregate outcomes are unlikely under current exposure levels in Japan **9)**」  
  → 日本での「糖尿病」の null や exposure level の根拠として 9) を出すと、読者は「日本における糖尿病の知見」と誤解する。9) は CVD の総説。
- 119行目: 「other investigations conducted at lower PM2.5 concentrations with limited geographic variation have failed to detect statistically significant associations **9)**」  
  → 同様に、糖尿病の null 研究として 9) を挙げるのは不適切。
- 145行目: 「Key strengths... **7),9)**」  
  → 9) はデータソースではなく CVD の総説のため、「strengths」の根拠として不整合。
- 149行目: 「narrow PM2.5 exposure range... **9),13),18)**」  
  → 日本の曝露範囲の文脈で 9) を出すと、糖尿病研究の対比として誤解される。

**判定**: **不一致**。糖尿病に関する日本での null 知見や曝露範囲の根拠として 9) を用いるのは不適切。削除するか、CVD の文脈に限定して言及する必要あり。

---

### 2. Ref 7) NIES AEROS — **データソースを「エビデンスの不均一性」の根拠として引用**

**文献の内容**: 大気汚染常時監視データ（AEROS）の説明。**データソース**であり、疫学論文ではない。

**引用箇所と問題点**:
- 51行目: 「However, evidence is heterogeneous across settings **4),5),6),7)**」  
  → 4),5),6) は系統レビュー・メタ解析で「evidence」として妥当。7) は監視データの出典であり、「evidence is heterogeneous」の根拠にはならない。

**判定**: **不一致**。7) は 65行目・145行目の「曝露データの出典」としてのみ用い、51行目の「evidence is heterogeneous」の引用からは削除すべき。

---

### 3. Ref 20) Chen et al. — Ontario（カナダ）を「メキシコ・韓国」と併記

**文献の内容**: "Ambient air pollution and incidence of type 2 diabetes: **The Ontario Diabetes Study**"（EHP 2013）. カナダ・オンタリオのコホート。

**引用箇所と問題点**:
- 118行目: 「Similarly, studies in **Mexico and Korea** have documented positive PM2.5–diabetes associations in settings with moderate-to-high pollution levels **18),20)**」  
  → 18)=韓国、19)=メキシコ。20) は**カナダ**であり、「Mexico and Korea」に含めると地理的・文脈的に誤り。

**判定**: **不一致**。「Mexico and Korea」の直後に 20) を置くのは不適切。20) を残すなら「North America (e.g., Ontario)」などと分けて記載するか、この文から 20) を外す必要あり。

---

### 4. Ref 22) Mitsuhashi et al. — 「null または borderline」のリストに陽性の日本研究を含む

**文献の内容**: "Fine particulate matter and **diabetes prevalence in Okayama, Japan**"（J Epidemiol 2019）. 日本・岡山で **陽性** の関連を報告。

**引用箇所と問題点**:
- 119行目: 「several European and North American cohorts and ecological studies have reported **null or borderline** associations, particularly at lower exposure ranges or in highly adjusted models **6),7),21),22)**」  
  → 22) は**日本**の研究であり、かつ**陽性**の関連。欧州・北米の「null or borderline」の例に 22) を入れるのは内容と矛盾。

**判定**: **不一致**。22) は同一段落内の「Within Japan... positive associations... **22),24),25)**」の引用でのみ用い、「null or borderline」のリスト（6),7),21)）からは削除すべき。

---

### 5. Ref 32) Kubo et al. — **心血管疾患入院**の文献を糖尿病論文の「Limitations」等で引用

**文献の内容**: "Association of PM2.5 exposure with **hospitalization for cardiovascular disease** in elderly individuals in Japan"（Sci Rep 2021）. アウトカムは**心血管疾患入院**であり、糖尿病ではない。

**引用箇所と問題点**:
- 145行目: 「Similar administrative data approaches have been successfully used in **PM2.5 health research** **32),33),34),35)**」  
  → 本論文は糖尿病。32) は CVD 入院の研究のため、「糖尿病関連の administrative data」の例として 32) を並べると主題がずれる。
- 149行目: 「Limitations include the ecological design... limited ability to detect small effects... **29),31),32)**」  
  → 29),31) は生態学・空間経済の方法論。32) は CVD 入院の実証研究であり、生態学デザインやサンプルサイズの「Limitations」を論じた文献ではない。

**判定**: **不一致**。糖尿病論文において、CVD 入院の 32) を「Limitations」や「administrative data の成功例」として引用するのは不適切。該当箇所から 32) を削除するか、CVD の文脈に限定して言及する必要あり。

---

### 6. Ref 33) Yorifuji et al. — **全死因入院・医療費**の文献を「生態学・空間」の方法論的根拠として引用

**文献の内容**: "Short-Term Associations of Ambient Fine Particulate Matter (PM2.5) with **All-Cause Hospital Admissions and Total Charges** in 12 Japanese Cities"（J Epidemiol 2020）. アウトカムは**全死因**の入院・医療費。短期影響。糖尿病ではない。

**引用箇所と問題点**:
- 131行目: 「multicollinearity... a challenge frequently noted in **ecological and spatial regression** analyses of chronic disease risk **29),33)**」  
  → 29) は生態学的研究の方法論で妥当。33) は時系列・短期効果の研究であり、生態学・空間回帰の方法論を論じた文献ではない。
- 137行目: 「sensitivity analyses, which targeted key sources of potential bias identified in **ecological and spatial epidemiology** **29),33)**」  
  → 同様に、33) は生態学・空間疫学の方法論的文献ではない。
- 145行目: 「Similar administrative data approaches... **32),33),34),35)**」  
  → 33) は入院・医療費の行政データを用いているが、アウトカムが全死因のため、糖尿病論文の「administrative data の成功例」としては主題がずれる。
- 155行目: 「high-resolution exposure models... to reduce **spatial misalignment** **30),33)**」  
  → 30) は測定誤差の概念で妥当。33) は 12 都市の短期効果であり、空間的ミスアラインメントを主題にした文献ではない。

**判定**: **不一致**。33) を「ecological and spatial regression」「ecological and spatial epidemiology」「spatial misalignment」の根拠として用いるのは不適切。該当箇所から 33) を削除するか、行政データ・短期効果の文脈に限定する必要あり。

---

## 一致と判定した主な引用（抜粋）

- 1), 2), 3): 糖尿病・代謝のメカニズム・リスク因子 — Introduction のメカニズム・リスクの記述と一致。
- 4), 5), 6): 糖尿病の系統レビュー・メタ解析・コホート — 「evidence is heterogeneous」やメタ解析の記述と一致。
- 8): NDB データ出典 — アウトカムのデータソースとして一致。
- 10)–17), 19), 24), 25), 26), 27), 28), 34), 35): 糖尿病・代謝・インスリン抵抗性・メカニズムの文献 — 引用文脈と一致。
- 18): 韓国コホート（糖尿病）— 「Korea」の記述と一致。
- 20): オンタリオ糖尿病研究 — 内容は糖尿病で一致するが、**地理表記（Mexico and Korea）との組み合わせが誤り**（上記 3 のとおり）。
- 21): ロサンゼルス・黒人女性の糖尿病・高血圧 — 北米のコホートとして妥当。
- 22): 岡山・糖尿病有病 — 「Japan, diabetes prevalence」の記述と一致（「null or borderline」のリストに含めている箇所のみ不一致）。
- 23): 妊娠糖尿病（日本）— 文脈と一致。
- 29), 30), 31): 生態学的研究・測定誤差・空間計量 — 方法論・限界の記述と一致。

---

## 修正推奨のまとめ

| 番号 | 修正内容 |
|------|----------|
| 9)   | 糖尿病の null・曝露範囲・strengths の根拠としての引用を削除。CVD の文脈で使う場合は「日本における PM2.5 と CVD」と明記するか、該当箇所から削除。 |
| 7)   | 51行目「evidence is heterogeneous across settings 4),5),6),7)」→「4),5),6)」に変更（7 を削除）。 |
| 20)  | 118行目「Mexico and Korea」に 20) を含めない。20) を残す場合は「and in North America (e.g., Ontario)」のように分けて記載。 |
| 22)  | 119行目「null or borderline... 6),7),21),22)」→「6),7),21)」に変更（22 を削除）。 |
| 32)  | 145行目・149行目から 32) を削除するか、CVD の行政データ研究である旨を短く注記。 |
| 33)  | 131, 137, 155行目から 33) を削除（生態学・空間・spatial misalignment の根拠としては不適切）。145行目は 32) と合わせて削除または注記を検討。 |

以上の修正により、引用元文献と引用箇所の内容が一致するようになる。
