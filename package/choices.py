from django.utils.translation import gettext_lazy as _


PKG_ORIGIN_MIGRATION = "MIGRATION"
PKG_ORIGIN_INGRESS_WITH_VALIDATION = "INGRESS_WITH_VALIDATION"
PKG_ORIGIN_INGRESS_WITHOUT_VALIDATION = "INGRESS_WITHOUT_VALIDATION"


PKG_ORIGIN = [
    (PKG_ORIGIN_MIGRATION, _("MIGRATION")),
    (PKG_ORIGIN_INGRESS_WITH_VALIDATION, _("INGRESS_WITH_VALIDATION")),
    (PKG_ORIGIN_INGRESS_WITHOUT_VALIDATION, _("INGRESS_WITHOUT_VALIDATION")),
]