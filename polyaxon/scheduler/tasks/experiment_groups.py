import logging

from constants.experiment_groups import ExperimentGroupLifeCycle
from db.getters import get_running_experiment_group, get_valid_experiment_group
from constants.experiments import ExperimentLifeCycle
from polyaxon.celery_api import app as celery_app
from polyaxon.settings import Intervals, RunnerCeleryTasks
from suggester import tasks
from scheduler.tasks.experiments import stop_experiment

_logger = logging.getLogger(__name__)


def _get_group_or_retry(experiment_group_id, task):
    experiment_group = get_valid_experiment_group(experiment_group_id=experiment_group_id)
    if experiment_group:
        return experiment_group

    # We retry if experiment group does not exist
    if task.request.retries < 2:
        _logger.info('Trying again for ExperimentGroup `%s`.', experiment_group_id)
        task.retry(countdown=Intervals.EXPERIMENTS_SCHEDULER)

    _logger.info('Something went wrong, '
                 'the ExperimentGroup `%s` does not exist anymore.', experiment_group_id)
    return None


@celery_app.task(name=RunnerCeleryTasks.EXPERIMENTS_GROUP_CREATE, bind=True, max_retries=None)
def create_group_experiments(self, experiment_group_id):
    experiment_group = _get_group_or_retry(experiment_group_id=experiment_group_id, task=self)
    if not experiment_group:
        return

    experiment_group.set_status(ExperimentGroupLifeCycle.RUNNING)
    tasks.create(experiment_group=experiment_group)


@celery_app.task(name=RunnerCeleryTasks.EXPERIMENTS_GROUP_STOP_EXPERIMENTS)
def stop_group_experiments(experiment_group_id, pending, message=None):
    experiment_group = get_running_experiment_group(experiment_group_id=experiment_group_id)
    if not experiment_group:
        return

    if pending:
        for experiment in experiment_group.pending_experiments:
            # Update experiment status to show that its stopped
            experiment.set_status(status=ExperimentLifeCycle.STOPPED, message=message)
    else:
        experiments = experiment_group.experiments.exclude(
            experiment_status__status__in=ExperimentLifeCycle.DONE_STATUS).distinct()
        for experiment in experiments:
            if experiment.is_running:
                stop_experiment.delay(experiment_id=experiment.id)
            else:
                # Update experiment status to show that its stopped
                experiment.set_status(status=ExperimentLifeCycle.STOPPED, message=message)

    experiment_group.set_status(ExperimentGroupLifeCycle.STOPPED)


@celery_app.task(name=RunnerCeleryTasks.EXPERIMENTS_GROUP_CHECK_FINISHED,
                 bind=True,
                 max_retries=None)
def check_group_finished(self, experiment_group_id):
    experiment_group = get_valid_experiment_group(experiment_group_id=experiment_group_id)
    if experiment_group.non_done_experiments.exists():
        self.retry(countdown=Intervals.EXPERIMENTS_SCHEDULER)
        return

    experiment_group.set_status(status=ExperimentGroupLifeCycle.SUCCEEDED)