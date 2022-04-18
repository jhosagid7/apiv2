from unittest.mock import MagicMock, call, patch
from rest_framework import status
from ..mixins import MarketingTestCase


class LeadTestSuite(MarketingTestCase):
    """
    🔽🔽🔽 Create with ActiveCampaignAcademy
    """
    @patch('breathecode.marketing.tasks.add_downloadable_slug_as_acp_tag.delay', MagicMock())
    def test_downloadable_saved__create__with_active_campaign_academy(self):
        """Test /downloadable/:id/user without auth"""
        from breathecode.marketing.tasks import add_downloadable_slug_as_acp_tag

        base = self.generate_models(academy=True, active_campaign_academy=True, skip_event=True)
        model = self.generate_models(downloadable=True, models=base)

        self.assertEqual(self.all_downloadable_dict(), [self.model_to_dict(model, 'downloadable')])
        self.assertEqual(add_downloadable_slug_as_acp_tag.delay.call_args_list, [call(1, 1)])
