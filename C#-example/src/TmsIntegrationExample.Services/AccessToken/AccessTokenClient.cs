// <copyright file="AccessTokenClient.cs" company="Engaged Technologies">
//     Copyright (c) Engaged Technologies. All rights reserved.
// </copyright>
// <summary>
//     EngagedTech API specific Access token client implementation
// </summary>

namespace TmsIntegrationExample.Services.AccessToken
{
    using IdentityModel;
    using IdentityModel.Client;
    using Microsoft.Extensions.Options;
    using System.Net.Http;
    using System.Text.Json;
    using System.Text;
    using System.Threading.Tasks;
    using TmsIntegrationExample.Services.AccessToken.Configuration;
    using TmsIntegrationExample.Services.Extensions;

    public class AccessTokenClient : IAccessTokenClient
    {
        private readonly AccessTokenConfiguration accessTokenConfiguration;
        private readonly IHttpClientFactory httpClientFactory;

        public AccessTokenClient(
            IOptions<AccessTokenConfiguration> accessTokenConfiguration,
            IHttpClientFactory httpClientFactory)
        {
            this.accessTokenConfiguration = accessTokenConfiguration.Value;
            this.httpClientFactory = httpClientFactory;
        }

        public static string HttpClientName => nameof(AccessTokenClient);

        public async Task<TokenResponse> GetAccessTokenAsync()
        {
            // Create an http client for all of the requests
            var httpClient = this.httpClientFactory.CreateClient(HttpClientName);

            // login
            await httpClient.PostAsync(
                this.accessTokenConfiguration.LoginSubPath,
                new StringContent(JsonSerializer.Serialize(new { this.accessTokenConfiguration.Email, this.accessTokenConfiguration.Password }), Encoding.UTF8, "application/json"));

            // instantiate state, code verifier, and verifier challenge
            var state = Helpers.CreateRandomString(128);
            var verifier = Helpers.CreateRandomString(128);
            var challenge = verifier.ToCodeChallenge();

            var discoveryDocumentResponse = await httpClient.GetDiscoveryDocumentAsync();

            // Create a relative url for requesting the authorization code
            var url = new RequestUrl(discoveryDocumentResponse.AuthorizeEndpoint).CreateAuthorizeUrl(
                responseType: "code",
                clientId: this.accessTokenConfiguration.ClientId,
                redirectUri: this.accessTokenConfiguration.RedirectUri,
                scope: $"openid {this.accessTokenConfiguration.Scope}",
                state: state,
                codeChallenge: challenge,
                codeChallengeMethod: OidcConstants.CodeChallengeMethods.Sha256);

            // Send the request for the authorization code and extract it from the location header
            var authorizeResponse = await httpClient.GetAsync(url);
            var code = System.Web.HttpUtility.ParseQueryString(authorizeResponse.Headers.Location.Query)["code"];

            // Request the access token
            var tokenResponse = await new TokenClient(httpClient, new TokenClientOptions { Address = discoveryDocumentResponse.TokenEndpoint, ClientId = this.accessTokenConfiguration.ClientId })
                .RequestAuthorizationCodeTokenAsync(
                    code,
                    this.accessTokenConfiguration.RedirectUri,
                    verifier);

            return tokenResponse;

        }
    }
}
