import json
import unittest

from tracker.proposal_tracker import ProposalTracker


class TestProposalTracker(unittest.TestCase):
    def setUp(self):
        with open('sample_data/latest.json') as f:
            self.data = json.load(f)

    def test_fetch_forum_proposals(self):
        tracker = ProposalTracker({"Test": "http://example.com"})
        # Patch fetch_forum_proposals to use sample data without network access
        def fake_fetch(name, url):
            results = []
            for t in self.data['topic_list']['topics']:
                results.append({
                    'id': t['id'],
                    'title': t['title'],
                    'created_at': t['created_at'],
                    'url': f"{url}/t/{t['slug']}",
                    'importance': 'Low',
                    'summary': t['title'][:100],
                })
            return results

        tracker.fetch_forum_proposals = fake_fetch
        tracker.update()
        self.assertIn('Test', tracker.state)
        self.assertEqual(len(tracker.state['Test']), 2)
        self.assertEqual(tracker.state['Test'][0]['id'], 1)
        self.assertIn('importance', tracker.state['Test'][0])
        self.assertIn('summary', tracker.state['Test'][0])


if __name__ == '__main__':
    unittest.main()

