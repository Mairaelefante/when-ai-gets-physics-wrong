import copy, json, math, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class PhysicsTests(unittest.TestCase):
    def test_implementation_present(self):
        self.assertTrue((ROOT/'reference.py').exists(), 'reference solver not implemented')

    def test_transport_invariants(self):
        from reference import transport
        b=4*100*28/(128**2)
        self.assertAlmostEqual(b,.68359375)
        self.assertEqual(transport(0,10,5,b),1)
        self.assertEqual(transport(2,1,5,b),0)
        self.assertGreater(transport(2,10,5,b),math.exp(-2))
        self.assertLess(transport(2,10,5,b),1)
        self.assertLess(transport(4,10,5,b),transport(2,10,5,b))

    def test_reference_independent_values(self):
        from reference import solve
        w=solve('W_geometry')
        self.assertAlmostEqual(w['plane_ratio'],115/94)
        self.assertAlmostEqual(w['finite_ratio'],55/94)
        r=solve('R_search')
        p=9.96e-8
        self.assertAlmostEqual(r['global_p'],1-(1-p)**1000,places=12)
        self.assertEqual(r['replication_decision'],'meets_threshold')

class GraderTests(unittest.TestCase):
    def test_correct_and_mutated_fields(self):
        from reference import solve, TASK_IDS
        from grader import grade
        for tid in TASK_IDS:
            a=solve(tid); a['explanation']='Derivation and scientific scope require manual review.'
            self.assertTrue(grade(tid,a)['structured_pass'],tid)
            self.assertEqual(grade(tid,a)['review_status'],'pending')
            for k,v in solve(tid).items():
                wrong=copy.deepcopy(a)
                wrong[k]=v+max(1,abs(v)) if type(v) in (int,float) else 'wrong'
                self.assertFalse(grade(tid,wrong)['structured_pass'],(tid,k))

    def test_boundary_and_valid_alternatives(self):
        from reference import solve
        from grader import grade, tolerance
        a=solve('W_geometry');a['explanation']='Use a conditional launch ensemble; no universal claim.'
        val=a['finite_ratio']; tol=tolerance(val)
        a['finite_ratio']=val+tol*.999
        a['notes']='Optional scientifically valid qualification.'
        self.assertTrue(grade('W_geometry',a)['structured_pass'])
        a['finite_ratio']=val+tol*1.001
        self.assertFalse(grade('W_geometry',a)['structured_pass'])
        del a['notes']; a['finite_ratio']=val
        a['finite_decision']='  Suppression  '
        self.assertTrue(grade('W_geometry',a)['structured_pass'])

    def test_malformed_not_physics_failures(self):
        from grader import grade
        for s in ['[]','null','{"a":1,"a":2}', '{"x":NaN}', '```json\n{}\n```']:
            self.assertEqual(grade('R_search',s)['status'],'format_error',s)

    def test_wrong_types_and_missing_fields(self):
        from reference import solve
        from grader import grade
        a=solve('R_search'); a['explanation']='Sufficient prose for manual adjudication.'
        for v in [True,'0.0001',float('inf'),float('nan')]:
            b=dict(a,global_p=v)
            self.assertFalse(grade('R_search',b)['structured_pass'])
            self.assertEqual(grade('R_search',b)['status'],'format_error')
        del a['global_p']
        self.assertEqual(grade('R_search',a)['status'],'format_error')

    def test_ungradable_prose_never_final_pass(self):
        from reference import solve
        from grader import grade
        a=solve('R_search');a['explanation']='The particles are proven to exist.'
        g=grade('R_search',a)
        self.assertTrue(g['structured_pass'])
        self.assertIsNone(g['scientific_pass'])
        self.assertEqual(g['review_status'],'pending')

if __name__=='__main__':unittest.main()

class RobustnessTests(unittest.TestCase):
    def test_huge_integer_is_format_error(self):
        from reference import solve
        from grader import grade
        a=solve('R_search');a['global_p']=10**400;a['explanation']='Large numeric format stress test.'
        self.assertEqual(grade('R_search',json.dumps(a))['status'],'format_error')

    def test_complete_authored_fixtures(self):
        from grader import grade
        for folder in ('correct','borderline'):
            for p in (ROOT/'fixtures'/folder).glob('*.json'):
                self.assertTrue(grade(p.stem,p.read_text())['structured_pass'],str(p))
        for p in (ROOT/'fixtures'/'authored_incorrect').glob('*.json'):
            tid='R_calibration' if p.stem.endswith('_prose') else p.stem
            g=grade(tid,p.read_text())
            if p.stem.endswith('_prose'):
                self.assertTrue(g['structured_pass']);self.assertIsNone(g['scientific_pass'])
            else:
                self.assertFalse(g['structured_pass']);self.assertEqual(g['scores']['local'],1)
