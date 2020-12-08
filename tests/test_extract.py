from whpool.extract.extract import PoolReport


def test_is_pool_report_true():
    # All POOL_REPORT_EXAMPLES should return true
    for index, report in enumerate(POOL_REPORT_EXAMPLES):
        assert PoolReport.is_pool_report(report), f"Report {index} not recognized as a pool report"


def test_is_pool_report_false():
    # All NONPOOL_REPORT_EXAMPLES should return false
    for index, report in enumerate(NONPOOL_REPORT_EXAMPLES):
        assert not PoolReport.is_pool_report(report), f"Report {index} incorrectly considered a pool report"


def test_process_pool_report_true():
    # All examples should return true
    examples = [
        {'title': 'Travel pool 11 -- some speech highlights/color',  'body': POOL_REPORT_EXAMPLES[0]},
        {'title': 'Travel pool 12 — lift from Marinette LZ', 'body': POOL_REPORT_EXAMPLES[1]},
        {'title': 'In-town pool report #8', 'body': POOL_REPORT_EXAMPLES[2]}
    ]

    for index, example in enumerate(examples):
        processed = {'PoolReport': 'true'}
        processed['Title'] = example['title']
        processed['processed_body_html'] = example['body']

        PoolReport.process_pool_report(processed)
        assert processed['PoolReport'] == 'true', f"Report {index} not recognized as a pool report"


def test_process_pool_report_false():
    # All examples should return false
    examples = [
        {'title': 'NOT REPORTABLE week ahead —',  'body': NONPOOL_REPORT_EXAMPLES[0]},
        {'title': 'FPPO/OTR - press entrance early tomorrow', 'body': NONPOOL_REPORT_EXAMPLES[1]},
        {'title': 'OTR/FPPO -- IMPORTANT COVID UPDATE (2)', 'body': NONPOOL_REPORT_EXAMPLES[2]},
        {'title': 'Test when key words not in title', 'body': NONPOOL_REPORT_EXAMPLES[0]},
        {'title': 'FPPO - Test when key words title but not in body', 'body': 'Call me Ishmael'}
    ]

    for index, example in enumerate(examples):
        processed = {'PoolReport': 'true'}
        processed['Title'] = example['title']
        processed['processed_body_html'] = example['body']

        PoolReport.process_pool_report(processed)
        assert processed['PoolReport'] == 'false', f"Report {index} incorrectly considered a pool report"


# All of the following are valid pool reports
POOL_REPORT_EXAMPLES = [
    '''\
    Behind the outdoor stage ... on the deck.
    The audience was a few hundred people.
    The president said the ...
    "The world is watching you," he told workers. "Our nation ..."

    Pool is being moved out near end of speech.
    ''',

    '''\
    At 4:48 local time headed back to Green Bay.
    ''',

    '''\
    Reporters gaggled on ... did a TV spot on ...

    Smith, however, declined to take questions as he walked back to the West Wing.
    ''',
]

# All of the following are not pool reports
NONPOOL_REPORT_EXAMPLES = [
    '''\
    FPPO version with times attached.
    ''',
    '''\
    Flagging for all, off the record.  From WH:

    NPS/USSS will be ..., from 4:30 AM to 7 AM. This will cause a ... when entering.
    ''',
    '''
     Reportable week ahead from the White House is below. FPPO version to follow, sometime later today."
    ''',
    '''
    OFF RECORD/FPPO

    Dear colleagues,

    We are writing ...
    '''
]
