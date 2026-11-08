import json, tempfile, unittest
from pathlib import Path
from make_comparison import build
from run_eval import run_trial
from reference import solve

class ComparisonTests(unittest.TestCase):
    def _response(self,payload):
        t=solve('R_search');t['explanation']='Explicitly authored fixture. NOT a model response.'
        return 200,{'status':'completed','model':'TEST_ONLY','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(t)}]}]}
    def test_no_fake_evidence_and_fixture_label(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);folder=d/'trials'
            run_trial('R_search',1,'TEST_ONLY',folder,self._response,test_only=True)
            a=build(folder,d/'empty.html');self.assertEqual(a['included'],0)
            self.assertIn('No eligible completed', (d/'empty.html').read_text())
            b=build(folder,d/'fixtures.html',True);self.assertEqual(b['included'],1)
            self.assertIn('DEMONSTRATION ONLY', (d/'fixtures.html').read_text())
            self.assertIn('not reviewed', (d/'fixtures.html').read_text().lower())
    def test_unreviewed_is_not_a_claim_of_failure(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);folder=d/'trials'
            run_trial('R_search',1,'TEST_ONLY',folder,self._response,test_only=True)
            b=build(folder,d/'fixtures.html',True)
            self.assertEqual(b['adjudicated_local_correct_global_wrong'],0)
if __name__=='__main__':unittest.main()
