// <copyright file="FormatExtensions.cs" company="Engaged Technologies">
//     Copyright (c) Engaged Technologies. All rights reserved.
// </copyright>
// <summary>
//    FormatExtensions class
// </summary>

namespace TmsIntegrationExample.Example.Extensions
{
    public static class FormatExtensions
    {
        public static string FormatContactPhone(this string phone)
        {
            if (string.IsNullOrWhiteSpace(phone))
            {
                return null;
            }

            var contactPhone = phone
                .Trim()
                .Replace("-", string.Empty)
                .Replace("(", string.Empty)
                .Replace(")", string.Empty)
                .Replace(" ", string.Empty);

            return contactPhone?.Length == 10 ? contactPhone : null;
        }

        public static string FormatCountryCode(this string countryName)
        {
            if (string.IsNullOrWhiteSpace(countryName))
            {
                return null;
            }

            return countryName switch
            {
                "US" or "USA" or "UNITED STATES" => "US",
                "MX" or "MEX" or "MEXICO" => "MX",
                "CA" or "CAN" or "CANAD" or "CANDA" or "CANADA" => "CA",
                "PUERTO RICO" or "PR" => "PR",
                _ => "US",
            };
        }
    }
}
