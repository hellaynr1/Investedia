"""Verify plotted financial relationships against the saved public source responses."""
import json,pathlib,unittest,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
class MarketLinks(unittest.TestCase):
 def test_city_coordinates(self):
  exchanges=json.loads(ROOT.joinpath('data/exchanges.json').read_text());raw=json.loads(ROOT.joinpath('tools/globe-news/market-sources/exchange-cities.json').read_text())
  for mic,row in raw['rows'].items():
   with self.subTest(mic=mic):
    self.assertEqual(exchanges[mic]['country'],row[8]);self.assertEqual(exchanges[mic]['coordinates']['latitude'],float(row[4]));self.assertEqual(exchanges[mic]['coordinates']['longitude'],float(row[5]));self.assertEqual(exchanges[mic]['coordinates']['source'],'https://www.geonames.org/'+row[0])
 def test_sources_and_values(self):
  read=lambda p:json.loads(ROOT.joinpath(p).read_text())
  data=read('assets/globe/market-links.json')
  for source in data['sources']:
   self.assertEqual(hashlib.sha256(ROOT.joinpath('tools/globe-news/market-sources',source['file']).read_bytes()).hexdigest(),source['sha256'])
   self.assertTrue(source['url'].startswith('https://'))
  trade=read('tools/globe-news/market-sources/comtrade-nigeria-2024.json')['data']
  portfolio={r['series_code']:r for r in read('tools/globe-news/market-sources/imf-cpis-nigeria.json')['series']['docs']}
  self.assertEqual(len(data['links']),20)
  for link in data['links']:
   with self.subTest(link=link['id']):
    self.assertNotEqual(link['from'],link['to']);self.assertGreater(link['value_usd'],0)
    if link['kind']=='trade':
     record=link['record'];raw=next(r for r in trade if r['partnerCode']==record['partner'])
     self.assertEqual((raw['period'],raw['flowCode'],raw['cmdCode']),('2024','X','TOTAL'))
     self.assertEqual(link['value_usd'],raw['primaryValue']);self.assertEqual(link['from'],'NG');self.assertEqual(link['year'],2024)
    else:
     raw=portfolio[link['series']];self.assertEqual(raw['dimensions']['INDICATOR'],'I_L_T_T_T_BP6_DV_USD')
     self.assertEqual(link['value_usd'],raw['value'][raw['period'].index('2023')])
     self.assertEqual(link['from'],raw['dimensions']['COUNTERPART_AREA']);self.assertEqual(link['to'],'NG');self.assertEqual(link['year'],2023)
if __name__=='__main__':unittest.main()
