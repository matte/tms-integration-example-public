// <copyright file="ServiceLevel.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     An enum of available service levels
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    public enum ServiceLevel
    {
        STANDARD = 0,

        GUARANTEED = 1,

        GUARANTEED_1030 = 2,

        GUARANTEED_1200 = 3,

        GUARANTEED_1500 = 4,

        GUARANTEED_PM = 5,

        GUARANTEED_1_DAY = 6,

        GUARANTEED_2_DAY = 7,
    }
}
