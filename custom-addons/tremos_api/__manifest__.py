{
    'name': 'Products,Users,Partners Syncronization',
    'version': '16.0.1.0.0',
    'summary': 'Products,Users,Partners Syncronization',
    'description': """ """,
    'category': 'Tools',
    'author': "Tremos",
    'company': 'Trend Motive Solutions',
    'maintainer': 'Tremos',
    'website': "https://trendmotivesolutions.com",
    'depends': ['base', 'contacts', 'stock', 'product'],
    'data': [
        "views/records_view.xml",
        "data/ir_cron.xml",
        "data/sequence.xml"
    ],
    'images': ['static/description/logo.jpeg'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
