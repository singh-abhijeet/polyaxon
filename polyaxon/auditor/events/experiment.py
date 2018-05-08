import auditor
from event_manager.events import experiment

auditor.register(experiment.ExperimentCreatedEvent)
auditor.register(experiment.ExperimentUpdatedEvent)
auditor.register(experiment.ExperimentDeletedEvent)
auditor.register(experiment.ExperimentViewedEvent)
auditor.register(experiment.ExperimentStoppedEvent)
auditor.register(experiment.ExperimentResumedEvent)
auditor.register(experiment.ExperimentRestartedEvent)
auditor.register(experiment.ExperimentCopiedEvent)
auditor.register(experiment.ExperimentNewStatusEvent)
auditor.register(experiment.ExperimentSucceededEvent)
auditor.register(experiment.ExperimentFailedEvent)
auditor.register(experiment.ExperimentResourcesViewedEvent)
auditor.register(experiment.ExperimentLogsViewedEvent)
auditor.register(experiment.ExperimentStatusesViewedEvent)
auditor.register(experiment.ExperimentJobsViewedEvent)

auditor.register(experiment.ExperimentJobViewedEvent)
auditor.register(experiment.ExperimentJobResourcesViewedEvent)
auditor.register(experiment.ExperimentJobLogsViewedEvent)
auditor.register(experiment.ExperimentJobStatusesViewedEvent)