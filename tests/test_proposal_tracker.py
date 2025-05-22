import json
import unittest

from tracker.proposal_tracker import ProposalTracker


class TestProposalTracker(unittest.TestCase):
    def setUp(self):
        with open('sample_data/latest.json') as f:
            self.data = json.load(f)

    def test_fetch_forum_proposals(self):
        tracker = ProposalTracker({"Test": "http://example.com"})
        # Patch fetch_latest_topics to return sample data
        tracker.fetch_forum_proposals = lambda name, url: [
            {
                'id': t['id'],
                'title': t['title'],
                'created_at': t['created_at'],
                'url': f"{url}/t/{t['slug']}"
            }
            for t in self.data['topic_list']['topics']
            if 'proposal' in t['title'].lower()
        ]
        tracker.update()
        self.assertIn('Test', tracker.state)
        self.assertEqual(len(tracker.state['Test']), 1)
        self.assertEqual(tracker.state['Test'][0]['id'], 1)


if __name__ == '__main__':
    unittest.main()
