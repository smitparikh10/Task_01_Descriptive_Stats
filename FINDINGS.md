# Findings: 2024 Facebook Political Ads

This note summarizes what the descriptive-statistics pass revealed about the dataset `fb_ads_president_scored_anon.csv`: a table of Facebook ad rows that reference 2024 U.S. presidential candidates. The analysis uses the same column-level logic implemented in `pure_python_stats.py` and cross-checked in `pandas_stats.py` (missingness rules, numeric parsing, and 95% threshold for treating a column as numeric).

## Scale and shape of the data

The extract contains **246,745 rows** and **40 columns**. Most core fields—identifiers, timing, spend, impressions, and the Illuminating-derived score columns—are fully populated in the sense of having a non-empty cell per row under the project’s missing-value token rules. Spot checks in the script outputs show selective gaps (for example, **ad_delivery_stop_time** is missing for about **0.87%** of rows, **bylines** for about **0.41%**, **estimated_audience_size** for about **0.23%**), which matters if you interpret “still running” or incomplete metadata differently from “missing stop time.”

There are thousands of distinct pages (**page_name** unique count on the order of **4.5k**), but row volume is *not* evenly spread: the modal page by row count is **Kamala Harris**, with on the order of **55k** ads in this slice—roughly one in five rows—followed by other high-frequency names such as **Donald J. Trump**, **Joe Biden**, and **The Daily Scroll**. That imbalance alone tells you that any row-level average will be dominated by a small set of heavy advertisers unless you aggregate or weight explicitly.

## Spending concentration

Using the **spend** field’s **lower bound** as a conservative proxy for money committed (the field is stored as text with currency formatting; the scripts parse it to a numeric lower bound), total lower-bound spend across the file is on the order of **$227.5M**. The **Kamala Harris** page accounts for roughly **$72.9M** of that lower-bound total by itself, and the **top five** pages together represent about **55.7%** of all lower-bound spend.

Substantively, that pattern describes a **heavy head, thinner middle**: a few entities account for most of the paid volume, while many smaller pages still appear often enough to matter for diversity of messaging but not for share of spend. Interpreting “who advertised” from row counts alone would therefore overstate how pluralistic the *spend* side of the market is.

## Timing is event-driven, not smooth

Spend and activity cluster on specific calendar days rather than spreading evenly. The **highest-spend ad creation date** in this file is **2024-10-27**, with other high days bunching in **late October**—consistent with endgame election advertising before voting. There is also a visible **July** spike (for example **2024-07-21** in the top days), which suggests that nomination-related or campaign-calendar events outside the final sprint still produce large bursts of paid activity.

For analysis, treat the time axis as **event-driven**: distributions by day will show spikes that reflect news cycles and strategic windows, not a stationary “baseline” rate of posting.

## Mentions, labels, and data quality

Candidate-related mention fields do not line up cleanly with spend shares. Part of that is **label fragmentation**: the same person can appear under multiple strings (for example **Donald Trump** vs **President Trump**), so frequency tables split what is substantively one entity. Part is **empty or hard-to-parse** mention representations in some rows. Even with those caveats, Trump- and Harris-related strings are both **high-frequency** and tied to **large** lower-bound spend totals in aggregate.

The takeaway for downstream work is procedural: **normalize entity strings** before comparing candidates by mention counts or before joining mentions to spend. Descriptive statistics on raw strings are still valuable—they surface duplication and missingness—but they are not yet a polished entity-level view.

## Closing takeaways

Together, the statistics portray a **highly concentrated spender landscape**, **spiky temporal advertising**, and **text-derived fields that need normalization** before causal or comparative claims. The profiling step is therefore partly a **data-quality audit**: how you define missing values, parse money, and infer numeric vs categorical columns directly changes the numbers you report and the stories you are allowed to tell from this export.
