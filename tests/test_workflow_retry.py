"""Retry only failed audio work; stale evidence must never reuse earlier checks."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from cbyp.workflow import VerificationRun


class WorkflowRetry(unittest.TestCase):
    def test_audio_checkpoint_and_changed_input(self):
        with tempfile.TemporaryDirectory() as folder:
            paths=[Path(folder)/name for name in ('note.png','camera.png','audio.wav')]
            for p in paths:p.write_bytes(b'fixture')
            session=MagicMock()
            session.note={'items':[{'quantity':2}]}
            session.look={};session.last_decision=None;session.opinions={};session.trace=[]
            session.call.return_value={'posted':False}
            order={'number':'PO','supplier':'S','product':'P','ordered':2,'received':0}
            with patch('cbyp.workflow.full_session',return_value=session), patch('cbyp.workflow.turns',side_effect=[TimeoutError(),['voice']]) as turns, patch('cbyp.workflow.understand_dialogue',return_value={'receiver':{'quantity':2}}):
                run=VerificationRun(*paths,order)
                with self.assertRaises(TimeoutError):run.run()
                self.assertTrue(run.retryable)
                result=run.run()
                session.read_delivery_note.assert_called_once()
                session.look_at_pallet.assert_called_once()
                session.count_cartons.assert_called_once()
                self.assertEqual(turns.call_count,2)
                self.assertEqual(sum(t['status']=='error' for t in result['timings']),1)
                self.assertFalse(result['erp_written'])
                paths[1].write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'Evidence changed'):run.run()
                self.assertFalse(run.retryable)
                self.assertEqual(turns.call_count,2)

    def test_interpretation_retry_does_not_transcribe_again(self):
        with tempfile.TemporaryDirectory() as folder:
            paths=[Path(folder)/name for name in ('n','c','a')]
            for p in paths:p.write_bytes(b'x')
            session=MagicMock();session.note={'items':[{'quantity':1}]};session.last_decision=None
            session.trace=[];session.opinions={};session.look={};session.call.return_value={}
            order={'number':'PO','supplier':'S','product':'P','ordered':1,'received':0}
            with patch('cbyp.workflow.full_session',return_value=session), patch('cbyp.workflow.turns',return_value=['voice']) as turns, patch('cbyp.workflow.understand_dialogue',side_effect=[TimeoutError(),{'receiver':{}}]):
                run=VerificationRun(*paths,order)
                with self.assertRaises(TimeoutError):run.run()
                run.run()
                turns.assert_called_once()
