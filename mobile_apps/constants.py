"""
Constants for mobile_apps app and related code
"""
MOBILE_APP_DEPLOYMENT_MECHANISMS = {
    'public_store': 1,
    'enterprise': 2,
    'ota': 3,
    'other': 4,
}


APP_DOWNLOAD_BANNER_IMAGES = {
    'mobile_iron': 'mobile_iron_badge',
    'ios_store': 'Badge.iOSAppStore',
    'android_store': 'Badge.PlayStore',
}

COMPANIES_MOBILE_APPS_MAP = {
    # Mckinsey and Company FF
    17: {
        'android': '',
        'ios': '',
        'tagline': 'Unlocking Leadership Potential',
        'background_image': '/static/image/mobile_popup/mcka_bg.png',
        'logo_image': '/static/image/mobile_popup/mcka_logo',
        'mobile_image': '/static/image/mobile_popup/mcka_devce',
        'download_banner_image': 'mobile_iron_badge'
    },
    # Chemours
    153: {
        'android': '',
        'ios': '',
        'tagline': '',
        'background_image': '/static/image/mobile_popup/rts_bg.png',
        'logo_image': '/static/image/mobile_popup/rts_logo',
        'mobile_image': '/static/image/mobile_popup/rts_device',
        'download_banner_image': 'Badge.iOSAppStore'
    }
}
