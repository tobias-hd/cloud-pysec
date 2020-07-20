import unittest
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


from sap.xssec.jwt_audience_validator import JwtAudienceValidator


class TestJwtAudienceValidator:

    XSUAA_BROKER_XSAPPNAME = "brokerplanmasterapp!b123"

    def test_constructor(self):
        self.jwt_audience_validator = JwtAudienceValidator(clientId="ABC")
        assert (self.jwt_audience_validator.clientIds).__len__() == 1


    def test_tokenAudienceMatchesClientId(self):
        clientIdFromToken = "clientid1"
        self.jwt_audience_validator = JwtAudienceValidator(clientIdFromToken)
        validation_result = self.jwt_audience_validator.validateToken(clientIdFromToken=clientIdFromToken)
        assert  validation_result == True

    def test_tokenAudienceMatchesAppId(self):
        audiencesfromToken=["appId!t1"]
        self.jwt_audience_validator = JwtAudienceValidator("sb-appId!t1")
        self.jwt_audience_validator.configureTrustedClientId('appId!t1')
        validation_result = self.jwt_audience_validator.validateToken(audiencesFromToken=audiencesfromToken)
        assert validation_result == True

    def test_tokenAudienceMatchesForeignClientId(self):
        audiencesfromToken = ["client", "foreignclient", "sb-test4!t1.data"]
        self.jwt_audience_validator = JwtAudienceValidator("any")
        self.jwt_audience_validator.configureTrustedClientId('foreignclient')
        validation_result = self.jwt_audience_validator.validateToken(audiencesFromToken=audiencesfromToken)
        assert validation_result == True

    def test_clientIdMatchesTokenAudienceWithoutDot(self):
        audiencesfromToken = ["client", "sb-test4!t1.data.x"]
        self.jwt_audience_validator = JwtAudienceValidator("sb-test4!t1")
        validation_result = self.jwt_audience_validator.validateToken(audiencesFromToken=audiencesfromToken)
        assert validation_result == True

    def test_tokenClientIdMatchesTrustedClientId(self):
        self.jwt_audience_validator = JwtAudienceValidator("client")
        validation_result = self.jwt_audience_validator.validateToken(clientIdFromToken="client")
        assert validation_result == True

    def test_brokerClientIdMatchesCloneAudience(self):
        audiencesfromToken = ["sb-f7016e93-8665-4b73-9b46-f99d7808fe3c!b446|" + self.XSUAA_BROKER_XSAPPNAME]
        self.jwt_audience_validator = JwtAudienceValidator("sb-" + self.XSUAA_BROKER_XSAPPNAME)
        self.jwt_audience_validator.configureTrustedClientId(self.XSUAA_BROKER_XSAPPNAME)
        validation_result = self.jwt_audience_validator.validateToken(audiencesFromToken=audiencesfromToken)
        assert validation_result == True

    def test_tokenClientIdMatchesTrustedBrokerClientId(self):
        clientIdFromToken = "sb-clone-app-id!b123|" + self.XSUAA_BROKER_XSAPPNAME
        self.jwt_audience_validator = JwtAudienceValidator(self.XSUAA_BROKER_XSAPPNAME)
        validation_result = self.jwt_audience_validator.validateToken(clientIdFromToken= clientIdFromToken)
        assert validation_result == True

    def test_tokenClientIdDoesNotMatchTrustedBrokerClientId(self):
        clientIdFromToken = "sb-clone-app-id!b123|xxx" + self.XSUAA_BROKER_XSAPPNAME
        self.jwt_audience_validator = JwtAudienceValidator(self.XSUAA_BROKER_XSAPPNAME)
        validation_result = self.jwt_audience_validator.validateToken(clientIdFromToken=clientIdFromToken)
        assert validation_result == False

    def test_brokerClientIdDoesNotMatchCloneAudience(self):
        audiencesfromToken = ["sb-f7016e93-8665-4b73-9b46-f99d7808fe3c!b446|ANOTHERAPP!b12"]
        self.jwt_audience_validator = JwtAudienceValidator("sb-" + self.XSUAA_BROKER_XSAPPNAME)
        self.jwt_audience_validator.configureTrustedClientId(self.XSUAA_BROKER_XSAPPNAME)
        validation_result = self.jwt_audience_validator.validateToken(audiencesFromToken=audiencesfromToken)
        assert validation_result == False

    def test_negativewhen_NoTokenAudienceMatches(self):
        audiencesfromToken = ["client", "foreignclient", "sb-test4!t1.data"]
        self.jwt_audience_validator = JwtAudienceValidator("any")
        self.jwt_audience_validator.configureTrustedClientId("anyOther")
        validation_result = self.jwt_audience_validator.validateToken(audiencesFromToken=audiencesfromToken)
        assert validation_result == False

    def test_shouldFilterEmptyAudiences(self):
        audiencesfromToken = [".", "test.", " .test2"]
        self.jwt_audience_validator = JwtAudienceValidator("any")
        validation_result = self.jwt_audience_validator.validateToken(audiencesFromToken=audiencesfromToken)
        assert validation_result == False

    def test_negative_Fails_when_TokenAudiencesAreEmpty(self):
        self.jwt_audience_validator = JwtAudienceValidator("any")
        validation_result = self.jwt_audience_validator.validateToken()
        assert validation_result == False

    def test_extractAudiencesFromTokenScopes(self):
        scopes = ["client.read", "test1!t1.read", "client.write", "xsappid.namespace.ns.write", "openid"]
        self.jwt_audience_validator = JwtAudienceValidator("client")
        audiences_result = self.jwt_audience_validator.extractAudiencesFromToken(scopesFromToken=scopes)
        assert len(audiences_result) == 3
        assert ('client') in audiences_result
        assert ('xsappid') in audiences_result
        assert ('test1!t1') in audiences_result
