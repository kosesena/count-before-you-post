import unittest
from cbyp.voice import validate_dialogue

class VoiceEvidence(unittest.TestCase):
    said=[{'speaker':'A','transcript':'Twelve delivered.'},
          {'speaker':'B','transcript':'I counted twelve. Two. Done.'}]
    def parsed(self, candidates):
        return {'receiver_speaker':'B','receiver_turn':self.said[1]['transcript'],
                'count_candidates':candidates,'receiver':{'quantity':12,'certain':True}}
    def test_two_possible_counts_are_uncertain(self):
        out=validate_dialogue(self.parsed([12,2]),self.said)
        self.assertFalse(out['receiver']['certain'])
        self.assertEqual(out['receiver']['quantity'],12)
    def test_missing_or_invented_turn_cannot_be_certain(self):
        for quote in ('','Twelve cartons.'):
            p=self.parsed([12]);p['receiver_turn']=quote
            self.assertFalse(validate_dialogue(p,self.said)['receiver']['certain'])
    def test_other_speaker_quote_does_not_ground_receiver(self):
        p=self.parsed([12]);p['receiver_turn']=self.said[0]['transcript']
        self.assertFalse(validate_dialogue(p,self.said)['receiver']['certain'])
    def test_empty_or_invalid_candidates_are_uncertain(self):
        for values in ([],[True],[-1],[11]):
            self.assertFalse(validate_dialogue(self.parsed(values),self.said)['receiver']['certain'])
    def test_supported_single_count_retains_uncertainty(self):
        p=self.parsed([12]);p['receiver']['certain']=False
        self.assertFalse(validate_dialogue(p,self.said)['receiver']['certain'])
    def test_supported_single_count_can_pass(self):
        self.assertTrue(validate_dialogue(self.parsed([12]),self.said)['receiver']['certain'])
