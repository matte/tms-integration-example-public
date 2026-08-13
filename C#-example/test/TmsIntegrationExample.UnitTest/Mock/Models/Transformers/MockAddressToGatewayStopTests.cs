// <copyright file="MockAddressToGatewayStopTests.cs" company="Engaged Technologies">
//     Copyright (c) Engaged Technologies. All rights reserved.
// </copyright>
// <summary>
//     Tests for the MockOrderToShipmentTests class
// </summary>

namespace TmsIntegrationExample.UnitTest.Mock.Models.Transformers
{
    using FluentAssertions;
    using TmsIntegrationExample.Example.Transformers;
    using TmsIntegrationExample.Services.MockApi.Model;
    using TmsIntegrationExample.Services.TmsGatewayApi.Model;
    using Xunit;

    public class MockAddressToGatewayStopTests
    {
        [Fact]
        public void MockAddressToGatewayStopTransformAsExpected()
        {
            var address = new Address
            {
                CorpAddressId = 19243,
                MailAddress1 = "1291 HARDIGREE ROAD",
                MailAddress2 = "WINDER, GA 30680-",
                MailCity = "WINDER",
                MailState = "GA",
                MailPostalCode = "30680",
                MailCountry = "USA",
                CentralPhoneNumber = "000-000-0000",
                CentralFaxNumber = "000-000-0000",
                PhysAddress1 = "1291 HARDIGREE ROAD",
                PhysAddress2 = "WINDER, GA 30680-",
                PhysAddress3 = "GA-BARROW",
                PhysCity = "WINDER",
                PhysState = "GA",
                PhysPostalCode = "30680",
                PhysCountry = "USA",
                AddressId = 26412,
                Name = "FOLEY PRODUCTS CO.",
            };

            var expectedStop = new Stop
            {
                Name = "FOLEY PRODUCTS CO.",
                Address1 = "1291 HARDIGREE ROAD",
                Address2 = "WINDER, GA 30680-",
                City = "WINDER",
                StateCode = "GA",
                PostalCode = "30680",
                CountryCode = "US",
                ContactPhone = "0000000000",
                ContactFax = "0000000000",
                SendEmail = true,
            };

            var result = new MockAddressToGatewayStop().Transform(address);

            result.Should().BeEquivalentTo(expectedStop);
        }

        [Fact]
        public void MockAddressToGatewayStopTransformFailsAsExpected()
        {
            var address = new Address
            {
                CorpAddressId = 19243,
                MailAddress1 = "1291 HARDIGREE ROAD",
                MailAddress2 = "WINDER, GA 30680-",
                MailCity = "WINDER",
                MailState = "GA",
                MailPostalCode = "30680",
                MailCountry = "USA",
                CentralPhoneNumber = "000-000-0000",
                CentralFaxNumber = "000-000-0000",
                PhysAddress1 = "1291 HARDIGREE ROAD",
                PhysAddress2 = "WINDER, GA 30680-",
                PhysAddress3 = "GA-BARROW",
                PhysCity = "WINDER",
                PhysState = "GA",
                PhysPostalCode = "30680",
                PhysCountry = "USA",
                AddressId = 26412,
                Name = "FOLEY PRODUCTS CO.",
            };

            var expectedStop = new Stop
            {
                Name = "FOLEY PRODUCTS CO.",
                Address1 = "1291 HARDIGREE ROAD",
                Address2 = "WINDER, GA 30680-",
                City = "WINDER",
                StateCode = "GA",
                PostalCode = "30680",
                CountryCode = "US",
                ContactPhone = "000-000-0000",
                ContactFax = "000-000-0000",
                SendEmail = true,
            };

            var result = new MockAddressToGatewayStop().Transform(address);
            result.Should().NotBeEquivalentTo(expectedStop);
        }
    }
}
