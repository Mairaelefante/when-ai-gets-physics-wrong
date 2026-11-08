import json, tempfile, unittest
from pathlib import Path

class HarnessTests(unittest.TestCase):
    def test_extract_preserves_all_output_text(self):
        from run_eval import extract_text
        r={'output':[{'type':'reasoning','summary':[{'text':'summary'}]}, {'type':'message','content':[{'type':'output_text','text':'one'}, {'type':'output_text','text':'two'}]}]}
        self.assertEqual(extract_text(r),'onetwo')
        self.assertEqual(extract_text({'output':[]}),'')

    def test_transcript_and_replay_with_explicit_test_transport(self):
        from run_eval import run_trial, replay
        from reference import solve
        def test_transport(payload):
            a=solve('R_search');a['explanation']='Synthetic test fixture, not a model response.'
            return 200,{'id':'TEST_ONLY','model':'TEST_ONLY','status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(a)}]}],'usage':{'input_tokens':1,'output_tokens':1}}
        with tempfile.TemporaryDirectory() as d:
            path=run_trial('R_search',1,'TEST_ONLY',Path(d),test_transport,test_only=True)
            a=json.loads(path.read_text())
            self.assertTrue(a['test_only']);self.assertEqual(a['status'],'completed')
            self.assertIn('request',a);self.assertIn('raw_response',a)
            result=replay(Path(d))
            self.assertEqual(result['eligible_model_trials'],0)
            self.assertEqual(result['test_fixture_trials'],1)
            with self.assertRaises(FileExistsError):run_trial('R_search',1,'TEST_ONLY',Path(d),test_transport,test_only=True)
            original=path.read_text()
            a['test_only']=False;path.write_text(json.dumps(a))
            self.assertEqual(replay(Path(d))['integrity_errors'],1)
            path.write_text(original);a=json.loads(original)
            a['request']['model']='tampered';path.write_text(json.dumps(a))
            self.assertEqual(replay(Path(d))['integrity_errors'],1)

    def test_api_error_is_not_reasoning_failure(self):
        from run_eval import run_trial,replay
        with tempfile.TemporaryDirectory() as d:
            run_trial('R_search',1,'TEST_ONLY',Path(d),lambda p:(429,{'error':{'message':'test rate limit'}}),test_only=True)
            a=replay(Path(d))
            self.assertEqual(a['api_errors'],1)
            self.assertEqual(a['structured_failures'],0)

if __name__=='__main__':unittest.main()

class CompletedMalformedResponseTests(unittest.TestCase):
    def test_huge_number_is_not_transport_error(self):
        from run_eval import run_trial
        from reference import solve
        def malformed_output(payload):
            a=solve('R_search');a['global_p']=10**400;a['explanation']='Out-of-range number test.'
            return 200,{'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(a)}]}]}
        with tempfile.TemporaryDirectory() as d:
            p=run_trial('R_search',1,'TEST_ONLY',Path(d),malformed_output,test_only=True)
            a=json.loads(p.read_text())
            self.assertEqual(a['status'],'completed')
            self.assertEqual(a['grade']['status'],'format_error')
