// <copyright file="IAccessTokenClient.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Interface for the getting and Access Token
// </summary>

namespace TmsIntegrationExample.Services.AccessToken
{
    using IdentityModel.Client;
    using System.Threading.Tasks;

    public interface IAccessTokenClient
    {
        Task<TokenResponse> GetAccessTokenAsync();
    }
}
