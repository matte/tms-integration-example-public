// <copyright file="TmsGatewayConfiguration.cs" company="Engaged Technologies">
// Copyright (c) Engaged Technologies. All rights reserved.
// </copyright>
// <summary>
//     Configuration class for AccessToken
// </summary>

namespace TmsIntegrationExample.Services.AccessToken.Configuration
{
    public class AccessTokenConfiguration
    {
        public System.Uri BaseAddress { get; set; }
        public string LoginSubPath { get; set; }
        public string Email { get; set; }
        public string Password { get; set; }
        public string ClientId { get; set; }
        public string RedirectUri { get; set; }
        public string Scope { get; set; }
    }
}
