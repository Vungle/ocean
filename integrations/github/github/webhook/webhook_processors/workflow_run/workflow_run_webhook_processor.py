from loguru import logger
from github.webhook.events import WORKFLOW_DELETE_EVENTS
from github.webhook.webhook_processors.workflow_run.base_workflow_run_webhook_processor import (
    BaseWorkflowRunWebhookProcessor,
)
from github.helpers.utils import enrich_with_organization, enrich_with_repository
from port_ocean.core.handlers.port_app_config.models import ResourceConfig
from port_ocean.core.handlers.webhook.webhook_event import (
    EventPayload,
    WebhookEventRawResults,
)


class WorkflowRunWebhookProcessor(BaseWorkflowRunWebhookProcessor):
    async def handle_event(
        self, payload: EventPayload, resource_config: ResourceConfig
    ) -> WebhookEventRawResults:
        action = payload["action"]
        repo = payload["repository"]
        workflow_run = payload["workflow_run"]
        organization = self.get_webhook_payload_organization(payload)["login"]

        logger.info(
            f"Processing workflow run event: {action} of organization: {organization}"
        )

        if not await self.should_process_repo_search(payload, resource_config):
            return WebhookEventRawResults(
                updated_raw_results=[], deleted_raw_results=[]
            )

        enriched = enrich_with_organization(
            enrich_with_repository(workflow_run, repo["name"], repo=repo),
            organization,
        )

        if action in WORKFLOW_DELETE_EVENTS:
            logger.info(
                f"Workflow run {workflow_run['name']} was deleted from organization: {organization}"
            )
            return WebhookEventRawResults(
                updated_raw_results=[], deleted_raw_results=[enriched]
            )

        logger.info(
            f"Workflow run {workflow_run['name']} of organization: {organization} was upserted"
        )

        return WebhookEventRawResults(
            updated_raw_results=[enriched], deleted_raw_results=[]
        )
