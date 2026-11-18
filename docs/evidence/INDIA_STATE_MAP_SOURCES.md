# India state-wise wheat context

This is observed agricultural context, separate from the project's national climate–nutrition index. No state-level F4, future yield loss, nutrient availability or deficiency has been estimated.

The ten rows in `data/external/india_state_wheat_2023_24.csv` were transcribed from **Agricultural Statistics at a Glance 2024–25**, Ministry of Agriculture & Farmers Welfare, Table 2.5(b), printed page 54. Both production and irrigation columns use **2023–24**. [Official source PDF](https://desagri.gov.in/wp-content/uploads/2024/11/Agricultural-Statisitcs-at-a-Glance-2024-25_कृषि-सांख्यिकी-एक-झलक-2024–25.pdf). Source accessed 18 November 2026. The table also contains 2024–25 production, which is deliberately not mixed with the 2023–24 irrigation column.

Uttar Pradesh, Madhya Pradesh and Punjab together account for 66.78% of national wheat production, summing the published shares. The six largest producers together account for 91.55%; each reports over 95% of wheat area irrigated. Himachal Pradesh reports 26.39% irrigation coverage but contributes 0.69% of national wheat production. This contrast illustrates the distinction between irrigation coverage and national production importance. Irrigated area does not measure water reliability, groundwater sustainability or protection from heat.

Map colours show published production shares and irrigation coverage. Unlisted states are grey, not zero. These figures contextualise the national wheat finding; they do not establish which state faces the largest future climate loss.

Boundaries: geoBoundaries gbOpen IND ADM1, 2011 reference, CC BY 2.5 IN. [Metadata](https://www.geoboundaries.org/api/current/gbOpen/IND/ADM1/). [Pinned simplified geometry](https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/9469f09/releaseData/gbOpen/IND/ADM1/geoBoundaries-IND-ADM1_simplified.geojson). These are historical boundary units; the ten mapped state names are matched explicitly, including Uttaranchal/Uttarakhand. The map is not a representation of current administrative changes elsewhere.

Implementation: `code/presentation_india_states.py`. The local repositories do not contain the ignored `cellmaps_*.npz`, `grids_*.npz` or `hazards_*.npz` outputs needed to aggregate project hazards by state. Adding state-level climate estimates would require recovering those files and overlaying state boundaries. State-level nutritional dependence would additionally need suitable food-supply or dietary data; national importance cannot simply be treated as state observations.
