// <copyright file="Helpers.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Class to generate authentication helpers
// </summary>

namespace TmsIntegrationExample.Services.Extensions
{

    using IdentityModel;
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Security.Cryptography;
    using System.Text;

    public static class Helpers
    {
        public static IEnumerable<char> GetChars(this char c, int length) =>
            Enumerable.Range(c, length).Select(i => (char)i);

        public static string CreateRandomString(int length)
        {
            var availableChars = new string('A'.GetChars(26)
                .Concat('a'.GetChars(26))
                .Concat('0'.GetChars(10)).ToArray());

            return new string(Enumerable.Range(0, length).Select(_ => availableChars[new Random().Next(availableChars.Length)]).ToArray());
        }

        public static string ToCodeChallenge(this string verifier)
        {
            using SHA256 sha256 = SHA256.Create();
            return Base64Url.Encode(sha256.ComputeHash(Encoding.UTF8.GetBytes(verifier)));
        }
    }
}
