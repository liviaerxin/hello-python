from celery import group, chord, chain, signature, Task
from celery.canvas import Signature
from celery.result import AsyncResult, allow_join_result, GroupResult, ResultSet

import time
from app.celery_task_app import ml_tasks
import uuid


def store(node):
    id_chain = []
    while node.parent:
        id_chain.append(node.id)
        node = node.parent
    id_chain.append(node.id)
    return id_chain


def restore(id_chain):
    id_chain.reverse()
    last_result = None
    for tid in id_chain:
        result = AsyncResult(tid)
        result.parent = last_result
        last_result = result
    return last_result


def run_chord():
    task = chord([ml_tasks.add.s(2, 2), ml_tasks.add.s(3, 3)])(ml_tasks.test_celery.s())
    print(f"{task.get()}")


def run_group():
    task: GroupResult = group(
        [ml_tasks.add.s(2, 2), ml_tasks.add.s(3, 3), ml_tasks.add.s(4, 4)]
    ).apply_async()
    print(f"#{task.id} {task.get()}")

    task.save()
    saved_result = GroupResult.restore(task.id)

    print(f"#{saved_result.id} {saved_result.get()}")


def run_chain():
    s1 = ml_tasks.add.s(4, 5)
    s2 = ml_tasks.add.s(6)
    s3 = ml_tasks.add.s(7)

    result: AsyncResult = chain(s1, s2, s3).apply_async()

    print(result.get())


def get_chain_graph():
    # result: AsyncResult = chord(group([tasks.add.s(2, 2), tasks.add.s(3, 3)]))(
    #     group([tasks.add.si(2, 2), tasks.add.si(3, 3)])
    # )
    # fmt: off
    task = chain(
            ml_tasks.add.s(2, 2), 
            ml_tasks.add.s(3)
        )
    # fmt: on
    result: AsyncResult = (
        task.freeze()
    )  # `freeze()` Dry run to give underlying running steps

    print(f"chain task: {task}")
    print(f"chain graph: {result.as_tuple()}")
    print(f"result: #[{result}]")


def get_group_graph():
    # fmt: off
    task = group(
        [
            ml_tasks.add.s(2, 2), 
            ml_tasks.add.s(3, 3)
        ])
    # fmt: on
    result: GroupResult = (
        task.freeze()
    )  # `freeze()` Dry run to give underlying running steps

    print(f"group task: {task}")
    print(f"group graph: {result.as_tuple()}")
    print(f"group: #[{result}]")


def get_chord_graph():
    task = chord(
        header=[ml_tasks.add.s(2, 2), ml_tasks.add.s(3, 3)], body=ml_tasks.add.si(4, 2)
    )
    # task = chord(header=[tasks.add.s(2, 2), tasks.add.s(3, 3)], body=group([tasks.add.si(4, 2), tasks.add.si(4, 3)]))
    result: AsyncResult = (
        task.freeze()
    )  # `freeze()` Dry run to give underlying running steps

    print(type(result.parent))
    print(f"chord task: {task}")
    print(f"chord graph: {result.as_tuple()}")
    print(f"chord: #[{result}]")


def run_chord_graph(dryrun=False, wait=True):
    # task = chord(header=[tasks.add.s(2, 2), tasks.add.s(3, 3)], body=tasks.add.si(4, 2))
    task = chord(
        header=[ml_tasks.add.s(2, 2), ml_tasks.add.s(3, 3)],
        body=group([ml_tasks.add.si(4, 2), ml_tasks.add.si(4, 3)]),
    )
    result: AsyncResult = (
        task.freeze() if dryrun else task.apply_async()
    )  # `freeze()` Dry run to give underlying running steps

    print(type(result.parent))
    print(f"chord task: {task}")
    print(f"chord graph: {result.as_tuple()}")
    print(f"chord: #[{result}]")
    if not dryrun and wait:
        print(f"chord: [{result.get()}]")


def run_signature(dryrun=False):
    task_id = str(uuid.uuid4())
    print(f"task_id#[{task_id}]")
    task: Signature = ml_tasks.progress.s(10).set(task_id=task_id)
    print(f"signature: #{task.id}")

    result: AsyncResult = task.freeze() if dryrun else task.apply_async()

    print(f"signature: {task}")
    print(f"signature: #[{result}]")
    if not dryrun:
        print(f"signature: [{result.get()}]")


def run_progress():
    t1: Signature = ml_tasks.progress.s(10).set(task_id=str(uuid.uuid4()))
    t2: Signature = ml_tasks.progress.s(5).set(task_id=str(uuid.uuid4()))

    # t3: Signature = ml_tasks.add.si(4, 4).set(task_id=str(uuid.uuid4()))
    # t4: Signature = ml_tasks.add.si(5, 5).set(task_id=str(uuid.uuid4()))
    t3: Signature = ml_tasks.test_celery.s().set(task_id=str(uuid.uuid4()))
    t4: Signature = ml_tasks.test_celery.s().set(task_id=str(uuid.uuid4()))

    task = chord(header=[t1, t2], body=group([t3, t4]))
    result: AsyncResult = task.apply_async()

    print(f"task: {task}")
    print(f"graph: {result.as_tuple()}")
    print(f"result: #[{result}]")

    res1 = AsyncResult(id=t1.id)
    res2 = AsyncResult(id=t2.id)
    res3 = AsyncResult(id=t3.id)
    res4 = AsyncResult(id=t4.id)

    ress = ResultSet(results=[res1, res2, res3, res4])

    while not result.ready():
        print(f"result #1, result[{res1.result}] status[{res1.status}]")
        print(f"result #2, result[{res2.result}] status[{res2.status}]")
        print(f"result #3, result[{res3.result}] status[{res3.status}]")
        print(f"result #4, result[{res4.result}] status[{res4.status}]")
        print(f"result set[#1, #2, #3, #4] {ress.completed_count()} {ress.ready()}")
        time.sleep(1)

    print(f"result #1, result[{res1.result}] status[{res1.status}]")
    print(f"result #2, result[{res2.result}] status[{res2.status}]")
    print(f"result #3, result[{res3.result}] status[{res3.status}]")
    print(f"result #4, result[{res4.result}] status[{res4.status}]")
    print(f"result set[#1, #2, #3, #4] {ress.completed_count()} {ress.ready()}")
    print(f"result: {result.get()}")


def run_two_chains():
    s1 = ml_tasks.add.s(4, 5).set(task_id=str(uuid.uuid4()))
    s2 = ml_tasks.add.s(6).set(task_id=str(uuid.uuid4()))
    c1 = chain(s1, s2)

    s3 = ml_tasks.add.si(10, 7).set(task_id=str(uuid.uuid4()))
    s4 = ml_tasks.add.s(7).set(task_id=str(uuid.uuid4()))
    c2 = chain(s3, s4)

    # result: AsyncResult = chain(c1, c2).apply_async()
    c3 = chain(c1, c2).apply_async()

    print(f"#s1[{s1.id}] #s2[{s2.id}]")
    print(f"#s3[{s3.id}] #s4[{s4.id}]")
    print(f"#c1[{s2.id}] #c2[{s4.id}] #c3[{c3.id}]")

    print(f"c1 result: {AsyncResult(id=s2.id).get()}")
    print(f"c2 result: {AsyncResult(id=s4.id).get()}")
    print(f"c3 result: {AsyncResult(id=c3.id).get()}")


if __name__ == "__main__":
    # run_chord_graph(dryrun=True)
    # run_chord_graph(dryrun=False, wait=True)
    # run_signature(dryrun=False)
    # run_progress()
    run_two_chains()
