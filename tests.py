import unittest
import pickle
from Symspell import check_query


class Tester(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Tester, self).__init__(*args, **kwargs)

        with open('en_index.p', 'rb') as fp:
            self.index = pickle.load(fp)

        with open('symindex.p', 'rb') as fp:
            self.sym_index = pickle.load(fp)

    def _run_test(self, token, result):
        assert check_query(token, self.index, self.sym_index) == result

    def test_transpose(self):
        self._run_test("yoghrut", {'yoghrut': 'yoghurt'})

    def test_insert(self):
        self._run_test("yoghuurt", {'yoghuurt': 'yoghurt'})

    def test_delete(self):
        self._run_test("yohurt", {'yohurt': 'yoghurt'})

    def test_replace(self):
        self._run_test("yaghurt", {'yaghurt': 'yoghurt'})

    def test_tr_ins(self):
        self._run_test("comfoortalbe", {'comfoortalbe': 'comfortable'})

    def test_tr_del(self):
        self._run_test("comfrtalbe", {'comfrtalbe': 'comfortable'})

    def test_tr_rep(self):
        self._run_test("comfartalbe", {'comfartalbe': 'comfortable'})

    def test_ins_ins(self):
        self._run_test("ayoghurta", {'ayoghurta': 'yoghurt'})

    def test_ins_del(self):
        self._run_test("pottector", {'pottector': 'protector'})

    def test_ins_rep(self):
        self._run_test("prattector", {'prattector': 'protector'})

    def test_del_del(self):
        self._run_test("prtectr", {'prtectr': 'protector'})

    def test_del_rep(self):
        self._run_test("prtectar", {'prtectar': 'protector'})

    def test_rep_rep(self):
        self._run_test("pratectar", {'pratectar': 'protector'})


if __name__ == '__main__':
    unittest.main()
