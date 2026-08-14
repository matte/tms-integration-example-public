// <copyright file="MockAddressToGatewayStop.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
// </copyright>
// <summary>
//      Transforms Mock API Address resouce to Gateway Stop resource
// </summary>

namespace TmsIntegrationExample.Example.Transformers
{
    using System.Collections.Generic;
    using TmsIntegrationExample.Example.Extensions;
    using TmsIntegrationExample.Services.MockApi.Model;
    using TmsIntegrationExample.Services.TmsGatewayApi.Model;

    public class MockAddressToGatewayStop
    {
        public Stop Transform(Address from)
        {
            if (from == null)
            {
                return null;
            }

            return new Stop
            {
                Name = from.Name,
                Address1 = from.PhysAddress1 ?? from.MailAddress1,
                Address2 = from.PhysAddress2 ?? from.MailAddress2,
                City = from.PhysCity ?? from.MailCity,
                StateCode = from.PhysState ?? from.MailState,
                PostalCode = from.PhysPostalCode ?? from.MailPostalCode,
                CountryCode = (from.PhysCountry ?? from.MailCountry).FormatCountryCode(),
                ContactPhone = from.CentralPhoneNumber.FormatContactPhone(),
                ContactEmails = string.IsNullOrEmpty(from.EmailAddress) ? null : new List<string> { from.EmailAddress },
                ContactFax = from.CentralFaxNumber.FormatContactPhone(),
                SendEmail = true,
            };
        }
    }
}
