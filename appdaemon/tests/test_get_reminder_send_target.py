from apps.reminder_service import get_send_target

CHAT_ID = '12345'

NOTIFY_DICT = {'notify': 'teledobbyme'}
NOTIFY_SERVICE = 'notify/teledobbyme'

TELEGRAM_DICT = {'chat_id': CHAT_ID}
TELEGRAM_SERVICE = 'telegram_bot/send_message'


def get_combined_dict():
    combined_dict = {}
    combined_dict.update(TELEGRAM_DICT)
    combined_dict.update(NOTIFY_DICT)
    return combined_dict


def test_get_reminder_target_notify_service():
    result = get_send_target(NOTIFY_DICT)
    assert NOTIFY_SERVICE == result.service()


def test_get_reminder_target_notify_kwargs():
    result = get_send_target(NOTIFY_DICT)
    assert {} == result.kwargs()


def test_get_reminder_target_telegram_service():
    result = get_send_target(TELEGRAM_DICT)
    assert TELEGRAM_SERVICE == result.service()


def test_get_reminder_target_telegram_kwargs():
    result = get_send_target(TELEGRAM_DICT)
    assert {'target': CHAT_ID} == result.kwargs()


def test_get_reminder_both_specified_returns_notify():
    result = get_send_target(get_combined_dict())
    assert NOTIFY_SERVICE == result.service()
